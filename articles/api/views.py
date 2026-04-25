from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models
from rest_framework.decorators import api_view
from articles.models import Article

from ..models import Article, Newsletter, Publisher, User
from .serializers import (
    ArticleSerializer,
    ArticleListSerializer,
    NewsletterSerializer,
    NewsletterDetailSerializer,
    PublisherSerializer
)

from ..permissions import (
    IsReaderOrJournalistOrEditor,
    IsEditor
)

@api_view(['POST'])
def approved_article_webhook(request):
    article_id = request.data.get('article_id')

    try:
        article = Article.objects.get(id=article_id)
        return Response({
            "status": "received",
            "article_id": article.id,
            "title": article.title
        }, status=status.HTTP_200_OK)

    except Article.DoesNotExist:
        return Response(
            {"error": "Article not found"},
            status=status.HTTP_404_NOT_FOUND
        )

# ---------------------------
# ARTICLES
# ---------------------------


class ArticleListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsReaderOrJournalistOrEditor]

    def get_queryset(self):
        return Article.objects.filter(approved=True)

    def get_serializer_class(self):
        return ArticleListSerializer if self.request.method == 'GET' else ArticleSerializer

    def perform_create(self, serializer):
        if self.request.user.role != 'Journalist':
            raise PermissionError("Only Journalists can create articles.")
        serializer.save(author=self.request.user)


class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [IsReaderOrJournalistOrEditor]

    def get_queryset(self):
        return Article.objects.all()


# ---------------------------
# SUBSCRIBED ARTICLES
# ---------------------------

class SubscribedArticlesView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        articles = Article.objects.filter(
            approved=True
        ).filter(
            models.Q(author__in=user.subscriptions_journalists.all()) |
            models.Q(publisher__in=user.subscriptions_publishers.all())
        ).distinct()

        return Response([
            {
                "id": a.id,
                "title": a.title,
                "content": a.content
            }
            for a in articles
        ])


# ---------------------------
# NEWSLETTERS
# ---------------------------

class NewsletterListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsReaderOrJournalistOrEditor]
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer


class NewsletterDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsReaderOrJournalistOrEditor]
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterDetailSerializer


# ---------------------------
# PUBLISHERS
# ---------------------------

class PublisherViewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsEditor()]
        return [IsAuthenticated()]
