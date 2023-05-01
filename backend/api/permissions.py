from rest_framework import permissions


class IsAuthOrListOnlyPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated


class IsAuthorOrGet(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method == 'GET' or request.user == obj.author
