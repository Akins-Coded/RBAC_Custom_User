# Django RBAC Application — Complete Build Guide

> Build a Django application with a custom user model and Role-Based Access Control (RBAC) using Django REST Framework.

---

## Architecture Overview

```
Incoming HTTP Request (browser / API client)
        │
        ▼
RBAC Middleware  ──── attaches roles & permissions to request
        │
        ▼
Authentication (JWT / Session)  ──── custom user model lookup
        │
        ▼
Permission Gate  ──── DRF permissions + decorators + object-level checks
   │          │
  403       pass
Denied        │
              ▼
       DRF View / ViewSet  ──── business logic, serializers
        │           │              │
        ▼           ▼              ▼
  Custom User    Role Model     Audit Log
  (AbstractUser  (Perms M2M     (Signals —
  + roles M2M)   via RolePerm)  role/perm changes)
        │           │              │
        └───────────┴──────────────┘
                    │
                    ▼
             SQLite Database (Development)
     users · roles · permissions · user_roles · audit_logs
```

---

## Recommended Folder Structure

```
project/
├── accounts/
│   ├── models.py        # CustomUser
│   ├── serializers.py
│   └── views.py         # assign_roles, profile endpoints
├── roles/
│   ├── models.py        # Role, Permission, RolePermission, AuditLog
│   ├── permissions.py   # IsSuperUser, HasRBACPermission
│   ├── decorators.py    # @rbac_required
│   ├── middleware.py    # RBACMiddleware
│   ├── validators.py    # validate_no_escalation
│   ├── signals.py       # audit log wiring
│   └── views.py         # RoleViewSet, PermissionViewSet
├── invoices/
│   ├── models.py        # Example resource
│   ├── views.py         # InvoiceViewSet with action permissions
└── rbac_project/
    └── settings.py      # AUTH_USER_MODEL, MIDDLEWARE, REST_FRAMEWORK
```

---

## Step 1 — Project Setup

Initialize the project and install dependencies:

```bash
pip install django djangorestframework djangorestframework-simplejwt \
            django-filter psycopg2-binary pytest-django pytest
```

---

## Step 2 — Custom User Model (`accounts` app)

```python
# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    roles = models.ManyToManyField('roles.Role', blank=True, related_name='users')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def has_rbac_perm(self, codename: str) -> bool:
        if self.is_superuser: return True
        return self.roles.filter(rolepermission__permission__codename=codename).exists()
```

---

## Step 3 — Role and Permission Models (`roles` app)

```python
# roles/models.py
from django.db import models

class Permission(models.Model):
    codename = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    module = models.CharField(max_length=100)
    action = models.CharField(max_length=20)

class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    permissions = models.ManyToManyField(Permission, through='RolePermission', blank=True)
    created_by = models.ForeignKey('accounts.CustomUser', null=True, on_delete=models.SET_NULL)

class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    granted_at = models.DateTimeField(auto_now_add=True)
```

---

## Step 4 — Audit Logging

Signals capture changes to roles and permissions automatically.

```python
# roles/signals.py
@receiver(post_save, sender=Role)
def log_role_save(sender, instance, created, **kwargs):
    AuditLog.objects.create(
        action='role_created' if created else 'role_updated',
        target=str(instance)
    )
```

---

## Step 5 — RBAC Middleware

Pre-fetches permissions lazily and attaches them to the request.

```python
# roles/middleware.py
class RBACMiddleware:
    def __call__(self, request):
        request.rbac_permissions = SimpleLazyObject(
            lambda: get_user_permissions(request.user)
        )
        return self.get_response(request)
```

---

## Step 6 — Testing

Run tests with `pytest`:

```bash
pytest
```

Tests cover:
- Superuser access
- Permission enforcement (view vs delete)
- Privilege escalation prevention
- Audit log generation
