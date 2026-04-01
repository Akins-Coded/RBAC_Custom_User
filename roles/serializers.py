from rest_framework import serializers
from .models import Role, Permission, AuditLog


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Permission
        fields = ['id', 'codename', 'name', 'module', 'action']


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.all(),
        write_only=True,
        source='permissions'
    )

    class Meta:
        model  = Role
        fields = ['id', 'name', 'description', 'permissions', 'permission_ids']


class AuditLogSerializer(serializers.ModelSerializer):
    actor = serializers.StringRelatedField()

    class Meta:
        model  = AuditLog
        fields = ['id', 'actor', 'action', 'target', 'metadata', 'timestamp']
