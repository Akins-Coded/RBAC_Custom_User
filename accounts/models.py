from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    roles = models.ManyToManyField(
        'roles.Role',
        blank=True,
        related_name='users'
    )

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']

    def has_rbac_perm(self, codename: str) -> bool:
        """Check if this user has a specific RBAC permission."""
        if self.is_superuser:
            return True
        return self.roles.filter(
            rolepermission__permission__codename=codename
        ).exists()

    def __str__(self):
        return self.email
