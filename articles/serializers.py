"""
Serializers for the News Application API.
Separate serializers for Article, User, Publisher, and Newsletter models.
"""
from rest_framework import serializers
from .models import User, Publisher, Article, Newsletter


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    Handles role-based field exposure.
    """
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role',
            'subscriptions_publishers', 'subscriptions_journalists',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']

    def create(self, validated_data):
        """
        Create user with password hashing and role-based group assignment.
        """
        password = validated_data.pop('password', None)
        subscriptions_publishers = validated_data.pop('subscriptions_publishers', [])
        subscriptions_journalists = validated_data.pop('subscriptions_journalists', [])

        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()

        # Handle many-to-many fields
        if subscriptions_publishers:
            user.subscriptions_publishers.set(subscriptions_publishers)
        if subscriptions_journalists:
            user.subscriptions_journalists.set(subscriptions_journalists)

        return user


class PublisherSerializer(serializers.ModelSerializer):
    """
    Serializer for Publisher model.
    """
    journalist_count = serializers.SerializerMethodField()

    class Meta:
        model = Publisher
        fields = ['id', 'name', 'journalists', 'editors', 'created_at', 'journalist_count']
        read_only_fields = ['id', 'created_at']

    def get_journalist_count(self, obj):
        return obj.journalists.count()


class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for Article model.
    Includes author and publisher details.
    """
    author_name = serializers.CharField(source='author.username', read_only=True)
    publisher_name = serializers.CharField(source='publisher.name', read_only=True, allow_null=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'author', 'author_name',
            'publisher', 'publisher_name', 'created_at', 'approved'
        ]
        read_only_fields = ['id', 'created_at', 'approved', 'author']

    def create(self, validated_data):
        """
        Create article with author set to requesting journalist.
        Articles start as unapproved (approved=False).
        """
        validated_data['approved'] = False
        return super().create(validated_data)


class ArticleListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for article list views.
    """
    author_name = serializers.CharField(source='author.username', read_only=True)
    publisher_name = serializers.CharField(source='publisher.name', read_only=True, allow_null=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'author_name', 'publisher_name', 'created_at']


class NewsletterSerializer(serializers.ModelSerializer):
    """
    Serializer for Newsletter model.
    """
    author_name = serializers.CharField(source='author.username', read_only=True)
    article_count = serializers.SerializerMethodField()

    class Meta:
        model = Newsletter
        fields = [
            'id', 'title', 'description', 'author', 'author_name',
            'articles', 'created_at', 'article_count'
        ]
        read_only_fields = ['id', 'created_at']

    def get_article_count(self, obj):
        return obj.articles.count()


class NewsletterDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Newsletter with nested article data.
    """
    author_name = serializers.CharField(source='author.username', read_only=True)
    articles = ArticleListSerializer(many=True, read_only=True)

    class Meta:
        model = Newsletter
        fields = [
            'id', 'title', 'description', 'author', 'author_name',
            'articles', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
