from rest_framework.exceptions import PermissionDenied


def validate_no_escalation(requesting_user, target_role):
    """
    Prevent non-superusers from granting permissions they do not possess.
    Call this inside perform_update and the user-role assignment endpoint.
    """
    if requesting_user.is_superuser:
        return

    role_perms = set(
        target_role.permissions.values_list('codename', flat=True)
    )
    user_perms = getattr(requesting_user, 'rbac_permissions', set())

    excess = role_perms - user_perms
    if excess:
        raise PermissionDenied(
            f"You cannot assign permissions you do not hold: {', '.join(excess)}"
        )
