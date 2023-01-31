from rest_framework import permissions


class IsManagerPermission(permissions.DjangoModelPermissions):

    def has_permission(self, request, view):
        if not request.user.groups.filter(name="manager").exists():
            return False
        return super().has_permission(request, view)

