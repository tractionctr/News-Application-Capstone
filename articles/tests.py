"""
Test suite for the News Application.
Tests role-based access, subscriptions, article approval, and signal behavior.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core import mail
from unittest.mock import patch, MagicMock
from .models import User, Publisher, Article, Newsletter

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for the custom User model."""

    def test_user_creation(self):
        """Test creating a user with default role."""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.assertEqual(user.role, 'Reader')
        self.assertEqual(str(user), 'testuser (Reader)')

    def test_user_with_journalist_role(self):
        """Test creating a journalist user."""
        user = User.objects.create_user(
            username='journalist',
            password='testpass123',
            role='Journalist'
        )
        self.assertEqual(user.role, 'Journalist')

    def test_user_with_editor_role(self):
        """Test creating an editor user."""
        user = User.objects.create_user(
            username='editor',
            password='testpass123',
            role='Editor'
        )
        self.assertEqual(user.role, 'Editor')

    def test_user_auto_group_assignment(self):
        """Test that user is automatically assigned to group based on role."""
        user = User.objects.create_user(
            username='groupuser',
            password='testpass123',
            role='Journalist'
        )
        groups = user.groups.all()
        self.assertEqual(groups.count(), 1)
        self.assertEqual(groups.first().name, 'Journalist')


class PublisherModelTest(TestCase):
    """Test cases for the Publisher model."""

    def test_publisher_creation(self):
        """Test creating a publisher."""
        publisher = Publisher.objects.create(name='Test Publisher')
        self.assertEqual(str(publisher), 'Test Publisher')

    def test_publisher_unique_name(self):
        """Test that publisher names are unique."""
        Publisher.objects.create(name='Test Publisher')
        with self.assertRaises(Exception):
            Publisher.objects.create(name='Test Publisher')


class ArticleModelTest(TestCase):
    """Test cases for the Article model."""

    def setUp(self):
        self.journalist = User.objects.create_user(
            username='journalist',
            password='testpass123',
            role='Journalist'
        )
        self.publisher = Publisher.objects.create(name='Test Publisher')

    def test_article_creation(self):
        """Test creating an article."""
        article = Article.objects.create(
            title='Test Article',
            content='Test content',
            author=self.journalist
        )
        self.assertEqual(str(article), 'Test Article')
        self.assertFalse(article.approved)

    def test_article_with_publisher(self):
        """Test creating an article with a publisher."""
        article = Article.objects.create(
            title='Publisher Article',
            content='Content',
            author=self.journalist,
            publisher=self.publisher
        )
        self.assertEqual(article.publisher, self.publisher)

    def test_article_author_must_be_journalist(self):
        """Test that article author must be a journalist."""
        reader = User.objects.create_user(
            username='reader',
            password='testpass123',
            role='Reader'
        )
        with self.assertRaises(Exception):
            Article.objects.create(
                title='Invalid Article',
                content='Content',
                author=reader
            )


class NewsletterModelTest(TestCase):
    """Test cases for the Newsletter model."""

    def setUp(self):
        self.journalist = User.objects.create_user(
            username='journalist',
            password='testpass123',
            role='Journalist'
        )

    def test_newsletter_creation(self):
        """Test creating a newsletter."""
        newsletter = Newsletter.objects.create(
            title='Test Newsletter',
            description='Test description',
            author=self.journalist
        )
        self.assertEqual(str(newsletter), 'Test Newsletter')

    def test_newsletter_articles(self):
        """Test adding articles to newsletter."""
        article = Article.objects.create(
            title='Article',
            content='Content',
            author=self.journalist
        )
        newsletter = Newsletter.objects.create(
            title='Newsletter',
            description='Description',
            author=self.journalist
        )
        newsletter.articles.add(article)
        self.assertIn(article, newsletter.articles.all())


class RoleBasedAccessTest(TestCase):
    """Test role-based access control."""

    def setUp(self):
        self.client = Client()
        self.reader = User.objects.create_user(
            username='reader',
            password='testpass123',
            role='Reader'
        )
        self.journalist = User.objects.create_user(
            username='journalist',
            password='testpass123',
            role='Journalist'
        )
        self.editor = User.objects.create_user(
            username='editor',
            password='testpass123',
            role='Editor'
        )
        self.article = Article.objects.create(
            title='Test Article',
            content='Content',
            author=self.journalist,
            approved=True
        )

    def test_reader_can_view_articles(self):
        """Test that readers can view approved articles."""
        self.client.login(username='reader', password='testpass123')
        response = self.client.get('/articles/')
        self.assertEqual(response.status_code, 200)

    def test_reader_cannot_create_article(self):
        """Test that readers cannot create articles."""
        self.client.login(username='reader', password='testpass123')
        response = self.client.post('/api/articles/', {
            'title': 'New Article',
            'content': 'Content'
        })
        self.assertIn(response.status_code, [403, 401])

    def test_journalist_can_create_article(self):
        """Test that journalists can create articles."""
        self.client.login(username='journalist', password='testpass123')
        response = self.client.post('/api/articles/', {
            'title': 'New Article',
            'content': 'Content'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_editor_can_approve_article(self):
        """Test that editors can approve articles."""
        unapproved = Article.objects.create(
            title='Unapproved',
            content='Content',
            author=self.journalist,
            approved=False
        )
        self.client.login(username='editor', password='testpass123')
        response = self.client.post(f'/articles/{unapproved.id}/approve/')
        self.assertEqual(response.status_code, 302)  # Redirect after success


class SubscriptionFilteringTest(TestCase):
    """Test subscription-based article filtering."""

    def setUp(self):
        self.reader = User.objects.create_user(
            username='reader',
            password='testpass123',
            role='Reader'
        )
        self.journalist1 = User.objects.create_user(
            username='journalist1',
            password='testpass123',
            role='Journalist'
        )
        self.journalist2 = User.objects.create_user(
            username='journalist2',
            password='testpass123',
            role='Journalist'
        )
        self.publisher1 = Publisher.objects.create(name='Publisher 1')
        self.publisher2 = Publisher.objects.create(name='Publisher 2')

        # Reader subscribes to journalist1 and publisher1
        self.reader.subscriptions_journalists.add(self.journalist1)
        self.reader.subscriptions_publishers.add(self.publisher1)

        # Create articles
        self.article1 = Article.objects.create(
            title='Article by subscribed journalist',
            content='Content',
            author=self.journalist1,
            approved=True
        )
        self.article2 = Article.objects.create(
            title='Article by unsubscribed journalist',
            content='Content',
            author=self.journalist2,
            approved=True
        )
        self.article3 = Article.objects.create(
            title='Article from subscribed publisher',
            content='Content',
            author=self.journalist2,
            publisher=self.publisher1,
            approved=True
        )
        self.article4 = Article.objects.create(
            title='Article from unsubscribed publisher',
            content='Content',
            author=self.journalist1,
            publisher=self.publisher2,
            approved=True
        )

    def test_reader_sees_subscribed_articles(self):
        """Test that reader sees articles from subscribed sources."""
        self.client.login(username='reader', password='testpass123')
        response = self.client.get('/api/articles/subscribed/')
        self.assertEqual(response.status_code, 200)
        article_ids = [a['id'] for a in response.data]
        self.assertIn(self.article1.id, article_ids)
        self.assertIn(self.article3.id, article_ids)

    def test_reader_does_not_see_unsubscribed_articles(self):
        """Test that reader doesn't see articles from unsubscribed sources."""
        self.client.login(username='reader', password='testpass123')
        response = self.client.get('/api/articles/subscribed/')
        article_ids = [a['id'] for a in response.data]
        self.assertNotIn(self.article2.id, article_ids)


class ArticleApprovalTest(TestCase):
    """Test article approval workflow."""

    def setUp(self):
        self.journalist = User.objects.create_user(
            username='journalist',
            password='testpass123',
            role='Journalist'
        )
        self.editor = User.objects.create_user(
            username='editor',
            password='testpass123',
            role='Editor'
        )
        self.client = Client()

    def test_article_created_unapproved(self):
        """Test that articles are created as unapproved."""
        self.client.login(username='journalist', password='testpass123')
        response = self.client.post('/api/articles/', {
            'title': 'New Article',
            'content': 'Content'
        }, content_type='application/json')
        self.assertEqual(response.data['approved'], False)

    def test_editor_can_approve(self):
        """Test that editor can approve an article."""
        article = Article.objects.create(
            title='Test Article',
            content='Content',
            author=self.journalist,
            approved=False
        )
        self.client.login(username='editor', password='testpass123')
        response = self.client.post(f'/articles/{article.id}/approve/')
        article.refresh_from_db()
        self.assertTrue(article.approved)

    def test_approved_articles_visible(self):
        """Test that approved articles are visible to readers."""
        article = Article.objects.create(
            title='Approved Article',
            content='Content',
            author=self.journalist,
            approved=True
        )
        reader = User.objects.create_user(
            username='reader',
            password='testpass123',
            role='Reader'
        )
        self.client.login(username='reader', password='testpass123')
        response = self.client.get('/api/articles/')
        article_ids = [a['id'] for a in response.data]
        self.assertIn(article.id, article_ids)


class SignalBehaviorTest(TestCase):
    """Test Django signal behavior on article approval."""

    def setUp(self):
        self.journalist = User.objects.create_user(
            username='journalist',
            password='testpass123',
            role='Journalist'
        )
        self.reader = User.objects.create_user(
            username='reader',
            password='testpass123',
            role='Reader',
            email='reader@example.com'
        )
        self.publisher = Publisher.objects.create(name='Test Publisher')
        self.editor = User.objects.create_user(
            username='editor',
            password='testpass123',
            role='Editor'
        )

        # Reader subscribes to journalist and publisher
        self.reader.subscriptions_journalists.add(self.journalist)
        self.reader.subscriptions_publishers.add(self.publisher)

    @patch('articles.signals.requests.post')
    def test_signal_sends_email_on_approval(self, mock_post):
        """Test that signal sends email when article is approved."""
        article = Article.objects.create(
            title='Test Article',
            content='Content',
            author=self.journalist,
            approved=False
        )

        # Approve the article
        article.approved = True
        article.save(update_fields=['approved'])

        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('New Article Approved', mail.outbox[0].subject)
        self.assertIn('reader@example.com', mail.outbox[0].to)

    @patch('articles.signals.requests.post')
    def test_signal_sends_api_request_on_approval(self, mock_post):
        """Test that signal sends POST request to API on approval."""
        mock_post.return_value = MagicMock(status_code=200)

        article = Article.objects.create(
            title='Test Article',
            content='Content',
            author=self.journalist,
            approved=False
        )

        article.approved = True
        article.save(update_fields=['approved'])

        mock_post.assert_called_once()
        call_args = mock_post.call_args[1]['json']
        self.assertEqual(call_args['article_id'], article.id)
        self.assertTrue(call_args['approved'])

    def test_signal_not_triggered_on_creation(self):
        """Test that signal is not triggered when article is created."""
        # Create approved article directly (shouldn't trigger signal on creation)
        article = Article.objects.create(
            title='Test Article',
            content='Content',
            author=self.journalist,
            approved=True
        )

        # No emails should be sent on creation
        self.assertEqual(len(mail.outbox), 0)


class PermissionDeniedTest(TestCase):
    """Test permission denied scenarios."""

    def setUp(self):
        self.client = Client()
        self.reader = User.objects.create_user(
            username='reader',
            password='testpass123',
            role='Reader'
        )
        self.journalist1 = User.objects.create_user(
            username='journalist1',
            password='testpass123',
            role='Journalist'
        )
        self.journalist2 = User.objects.create_user(
            username='journalist2',
            password='testpass123',
            role='Journalist'
        )
        self.editor = User.objects.create_user(
            username='editor',
            password='testpass123',
            role='Editor'
        )

        self.article = Article.objects.create(
            title='Test Article',
            content='Content',
            author=self.journalist1,
            approved=True
        )

    def test_reader_cannot_update_article(self):
        """Test that readers cannot update articles."""
        self.client.login(username='reader', password='testpass123')
        response = self.client.put(
            f'/api/articles/{self.article.id}/',
            {'title': 'Updated'},
            content_type='application/json'
        )
        self.assertIn(response.status_code, [403, 401])

    def test_journalist_cannot_update_others_article(self):
        """Test that journalists cannot update other journalists' articles."""
        self.client.login(username='journalist2', password='testpass123')
        response = self.client.put(
            f'/api/articles/{self.article.id}/',
            {'title': 'Updated'},
            content_type='application/json'
        )
        self.assertIn(response.status_code, [403, 404])

    def test_journalist_cannot_delete_others_article(self):
        """Test that journalists cannot delete other journalists' articles."""
        self.client.login(username='journalist2', password='testpass123')
        response = self.client.delete(f'/api/articles/{self.article.id}/')
        self.assertIn(response.status_code, [403, 404])

    def test_editor_can_update_any_article(self):
        """Test that editors can update any article."""
        self.client.login(username='editor', password='testpass123')
        response = self.client.put(
            f'/api/articles/{self.article.id}/',
            {'title': 'Updated Title'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_editor_can_delete_any_article(self):
        """Test that editors can delete any article."""
        self.client.login(username='editor', password='testpass123')
        response = self.client.delete(f'/api/articles/{self.article.id}/')
        self.assertEqual(response.status_code, 204)


class NewsletterPermissionTest(TestCase):
    """Test newsletter permissions."""

    def setUp(self):
        self.client = Client()
        self.reader = User.objects.create_user(
            username='reader',
            password='testpass123',
            role='Reader'
        )
        self.journalist = User.objects.create_user(
            username='journalist',
            password='testpass123',
            role='Journalist'
        )
        self.editor = User.objects.create_user(
            username='editor',
            password='testpass123',
            role='Editor'
        )

        self.newsletter = Newsletter.objects.create(
            title='Test Newsletter',
            description='Description',
            author=self.journalist
        )

    def test_reader_cannot_create_newsletter(self):
        """Test that readers cannot create newsletters."""
        self.client.login(username='reader', password='testpass123')
        response = self.client.post('/api/newsletters/', {
            'title': 'New Newsletter',
            'description': 'Description'
        }, content_type='application/json')
        self.assertIn(response.status_code, [403, 401])

    def test_journalist_can_create_newsletter(self):
        """Test that journalists can create newsletters."""
        self.client.login(username='journalist', password='testpass123')
        response = self.client.post('/api/newsletters/', {
            'title': 'New Newsletter',
            'description': 'Description'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_journalist_cannot_update_others_newsletter(self):
        """Test that journalists cannot update others' newsletters."""
        self.client.login(username='reader', password='testpass123')
        response = self.client.put(
            f'/api/newsletters/{self.newsletter.id}/',
            {'title': 'Updated'},
            content_type='application/json'
        )
        self.assertIn(response.status_code, [403, 404])

    def test_editor_can_update_any_newsletter(self):
        """Test that editors can update any newsletter."""
        self.client.login(username='editor', password='testpass123')
        response = self.client.put(
            f'/api/newsletters/{self.newsletter.id}/',
            {'title': 'Updated Title'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
