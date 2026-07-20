from rest_framework.permissions import BasePermission
from .models import UserProfile, ROLE_PERMISSIONS


def get_user_permissions(user):
    try:
        profile = user.profile
        return ROLE_PERMISSIONS.get(profile.role, ROLE_PERMISSIONS['viewer']), profile.role
    except UserProfile.DoesNotExist:
        return ROLE_PERMISSIONS['viewer'], 'viewer'


class HasPermission(BasePermission):
    required_permission = None

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        perms, role = get_user_permissions(request.user)
        if self.required_permission is None:
            return True
        return self.required_permission in perms


class IsRoot(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        _, role = get_user_permissions(request.user)
        return role == 'root'


class CanCreateList(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        perms, _ = get_user_permissions(request.user)
        return 'create_list' in perms


class CanDeleteList(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        perms, _ = get_user_permissions(request.user)
        return 'delete_list' in perms


class CanEditList(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        perms, _ = get_user_permissions(request.user)
        return 'edit_list' in perms
