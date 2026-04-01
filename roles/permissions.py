from rest_framework.permissions import BasePermission


class IsSuperUser(BasePermission):
    """Grants access only to Django superusers."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class HasRBACPermission(BasePermission):
    """
    Views declare a required_permission codename:

        class InvoiceViewSet(viewsets.ModelViewSet):
            required_permission = 'invoices.view'

    The permission is checked against the user's assigned roles.
    """

    def has_permission(self, request, view):
        codename = getattr(view, 'required_permission', None)
        if not codename:
            return False
        return (
            request.user.is_authenticated
            and request.user.has_rbac_perm(codename)
        )
