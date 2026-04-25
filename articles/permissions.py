"""
Custom permission classes for role-based access control.
Enforces permissions based on user roles: Reader, Journalist, Editor.
"""
from rest_framework import permissions


class IsReader(permissions.BasePermission):
    """
    Permission class for Reader role.
    Readers can only view articles and newsletters.
    """
    message = "Readers can only view content."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Reader'

    def has_object_permission(self, request, view, obj):
        # Readers can only view
        return request.method in permissions.SAFE_METHODS


class IsJournalist(permissions.BasePermission):
    """
    Permission class for Journalist role.
    Journalists can create, update, delete their own articles and newsletters.
    """
    message = "Journalists can only manage their own content."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Journalist'

    def has_object_permission(self, request, view, obj):
        # Allow safe methods for viewing
        if request.method in permissions.SAFE_METHODS:
            return True
        # For write operations, check ownership
        if hasattr(obj, 'author'):
            return obj.author == request.user
        return False


class IsEditor(permissions.BasePermission):
    message = "Only Editors can perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "Editor"

    def has_object_permission(self, request, view, obj):
        return True


class IsJournalistOrEditor(permissions.BasePermission):
    """
    Permission class for Journalist or Editor roles.
    Journalists can manage own content, Editors can manage all content.
    """
    message = "Only Journalists or Editors can perform this action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['Journalist', 'Editor']
        )

    def has_object_permission(self, request, view, obj):
        # Safe methods allowed for both
        if request.method in permissions.SAFE_METHODS:
            return True

        # Editors can do anything
        if request.user.role == 'Editor':
            return True

        # Journalists can only modify their own content
        if hasattr(obj, 'author'):
            return obj.author == request.user

        return False


class IsReaderOrJournalistOrEditor(permissions.BasePermission):
    """
    Allow access to Readers, Journalists, and Editors.
    Readers can view only, Journalists/Editors have more permissions.
    """
    message = "Authentication required."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['Reader', 'Journalist', 'Editor']
        )

    def has_object_permission(self, request, view, obj):
        # Safe methods for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write operations only for Journalists (own) or Editors (any)
        if request.user.role == 'Editor':
            return True

        if request.user.role == 'Journalist' and hasattr(obj, 'author'):
            return obj.author == request.user

        return False


class IsAuthenticatedWithRole(permissions.BasePermission):
    """
    Base permission that checks authentication and valid role.
    """
    message = "Authentication required with valid role."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['Reader', 'Journalist', 'Editor']
        )
