from rest_framework import permissions


class AuthorOnlyPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.user

    def has_permission(self, request, view):
        return True

