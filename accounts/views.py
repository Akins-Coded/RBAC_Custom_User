from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from roles.permissions import IsSuperUser
from roles.validators import validate_no_escalation
from roles.models import Role, AuditLog
from .models import CustomUser
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes


@extend_schema(
    summary="Assign roles to a user",
    description="Assign one or more roles to a user. Requires superuser privileges. Prevents privilege escalation.",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'role_ids': {
                    'type': 'array',
                    'items': {'type': 'integer'},
                    'description': 'List of role IDs to assign'
                }
            },
            'required': ['role_ids']
        }
    },
    responses={
        200: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
    }
)
@api_view(['POST'])
@permission_classes([IsSuperUser])
def assign_roles(request, user_id):
    """
    Assign one or more roles to a user.
    Body: { "role_ids": [1, 2, 3] }
    """
    try:
        user = CustomUser.objects.get(pk=user_id)
    except CustomUser.DoesNotExist:
        return Response({'detail': 'User not found.'}, status=404)

    role_ids = request.data.get('role_ids', [])
    roles    = Role.objects.filter(pk__in=role_ids)

    for role in roles:
        validate_no_escalation(request.user, role)

    user.roles.set(roles)

    AuditLog.objects.create(
        actor=request.user,
        action='role_assigned_to_user',
        target=str(user),
        metadata={'role_ids': role_ids}
    )

    return Response({'detail': 'Roles updated successfully.'})
