from django.db import models


class Permission(models.Model):
    codename = models.CharField(max_length=100, unique=True)  # e.g. "invoices.view"
    name     = models.CharField(max_length=255)
    module   = models.CharField(max_length=100)   # e.g. "invoices"
    action   = models.CharField(max_length=20)    # view | create | edit | delete

    def __str__(self):
        return self.codename


class Role(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(
        Permission,
        through='RolePermission',
        blank=True
    )
    created_by  = models.ForeignKey(
        'accounts.CustomUser',
        null=True,
        on_delete=models.SET_NULL,
        related_name='created_roles'
    )

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    role       = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('role', 'permission')


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('role_created',          'Role created'),
        ('role_updated',          'Role updated'),
        ('role_deleted',          'Role deleted'),
        ('perm_assigned',         'Permission assigned'),
        ('perm_removed',          'Permission removed'),
        ('role_assigned_to_user', 'Role assigned to user'),
    ]
    actor     = models.ForeignKey(
        'accounts.CustomUser',
        null=True,
        on_delete=models.SET_NULL
    )
    action    = models.CharField(max_length=50, choices=ACTION_CHOICES)
    target    = models.CharField(max_length=255)   # human-readable description
    metadata  = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.timestamp}] {self.actor} → {self.action} on {self.target}"
