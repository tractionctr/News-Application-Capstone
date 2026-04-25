"""
Django admin configuration for the News Application.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Publisher, Article, Newsletter


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin configuration for custom User model.
    """
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
        ('Subscriptions', {'fields': ('subscriptions_publishers', 'subscriptions_journalists')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    """
    Admin configuration for Publisher model.
    """
    list_display = ['name', 'created_at']
    filter_horizontal = ['journalists', 'editors']
    search_fields = ['name']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """
    Admin configuration for Article model.
    """
    list_display = ['title', 'author', 'publisher', 'approved', 'created_at']
    list_filter = ['approved', 'created_at', 'publisher']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at']

    def save_model(self, request, obj, form, change):
        """
        Set author automatically if not set.
        """
        if not obj.pk and not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """
    Admin configuration for Newsletter model.
    """
    list_display = ['title', 'author', 'created_at']
    list_filter = ['created_at', 'author']
    search_fields = ['title', 'description']
    filter_horizontal = ['articles']
