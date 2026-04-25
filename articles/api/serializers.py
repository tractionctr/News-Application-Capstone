from rest_framework import serializers
from ..models import Article, Newsletter, Publisher, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role']


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Article
        fields = '__all__'


class ArticleListSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username')

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author', 'created_at']


class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = '__all__'


class NewsletterDetailSerializer(serializers.ModelSerializer):
    articles = ArticleListSerializer(many=True, read_only=True)

    class Meta:
        model = Newsletter
        fields = '__all__'
