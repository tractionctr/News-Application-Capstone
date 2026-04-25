from django.urls import path
from articles.api.views import (
    ArticleListCreateView,
    ArticleDetailView,
    NewsletterListCreateView,
    NewsletterDetailView,
    SubscribedArticlesView,
    approved_article_webhook,
)

urlpatterns = [
    path('articles/', ArticleListCreateView.as_view()),
    path('articles/<int:pk>/', ArticleDetailView.as_view()),
    path('articles/subscribed/', SubscribedArticlesView.as_view()),

    path('newsletters/', NewsletterListCreateView.as_view()),
    path('newsletters/<int:pk>/', NewsletterDetailView.as_view()),

    path('approved/', approved_article_webhook),
]