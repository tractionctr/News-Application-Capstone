"""
Django app configuration for articles app.
"""
from django.apps import AppConfig


class ArticlesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'articles'

    def ready(self):
        """
        Import signals when app is ready.
        This ensures signal handlers are registered.
        """
        import articles.signals
