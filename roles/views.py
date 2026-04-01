from rest_framework import viewsets
from .models import Role, Permission
from .serializers import RoleSerializer, PermissionSerializer
from .permissions import IsSuperUser


class RoleViewSet(viewsets.ModelViewSet):
    """
    Full CRUD on roles.
    Only superusers can manage roles.
    """
    queryset         = Role.objects.prefetch_related('permissions')
    serializer_class = RoleSerializer
    permission_classes = [IsSuperUser]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List available permissions.
    Only superusers can view the full list of permissions.
    """
    queryset         = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsSuperUser]
