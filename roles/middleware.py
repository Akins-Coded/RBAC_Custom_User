from django.utils.functional import SimpleLazyObject


def get_user_permissions(user):
    """Return the set of permission codenames for a given user."""
    if not user.is_authenticated or user.is_superuser:
        return set()
    return set(
        user.roles
            .prefetch_related('rolepermission_set__permission')
            .values_list('rolepermission__permission__codename', flat=True)
    )


class RBACMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Lazily evaluated — only queries the DB if something accesses it
        perms = SimpleLazyObject(
            lambda: get_user_permissions(request.user)
        )
        request.rbac_permissions = perms
        if request.user.is_authenticated:
            request.user.rbac_permissions = perms
        return self.get_response(request)
