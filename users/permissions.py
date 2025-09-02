from rest_framework import permissions

class IsGroupAdmin(permissions.BasePermission):
    """
    Allows access only to authenticated users with role == 'Gat_Adhikari'.
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "Gat_Adhikari"
        )
