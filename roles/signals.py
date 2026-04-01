from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Role, RolePermission, AuditLog


@receiver(post_save, sender=Role)
def log_role_save(sender, instance, created, **kwargs):
    AuditLog.objects.create(
        action='role_created' if created else 'role_updated',
        target=str(instance),
        metadata={'role_id': instance.pk}
    )


@receiver(post_delete, sender=Role)
def log_role_delete(sender, instance, **kwargs):
    AuditLog.objects.create(
        action='role_deleted',
        target=str(instance),
        metadata={'role_id': instance.pk}
    )


@receiver(post_save, sender=RolePermission)
def log_perm_assigned(sender, instance, created, **kwargs):
    if created:
        AuditLog.objects.create(
            action='perm_assigned',
            target=f"{instance.role} → {instance.permission}",
            metadata={
                'role_id': instance.role_id,
                'permission_codename': instance.permission.codename
            }
        )


@receiver(post_delete, sender=RolePermission)
def log_perm_removed(sender, instance, **kwargs):
    AuditLog.objects.create(
        action='perm_removed',
        target=f"{instance.role} → {instance.permission}",
        metadata={
            'role_id': instance.role_id,
            'permission_codename': instance.permission.codename
        }
    )
