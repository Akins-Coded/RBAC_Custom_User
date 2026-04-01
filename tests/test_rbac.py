import pytest
from django.contrib.auth import get_user_model
from roles.models import Role, Permission
from invoices.models import Invoice

from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def superuser(db):
    return User.objects.create_superuser(
        email='admin@example.com', password='pass', username='admin'
    )


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        email='user@example.com', password='pass', username='user'
    )


@pytest.fixture
def invoice_viewer_role(db):
    perm = Permission.objects.create(
        codename='invoices.view', name='View Invoices',
        module='invoices', action='view'
    )
    role = Role.objects.create(name='Invoice Viewer')
    role.permissions.add(perm)
    return role


def test_superuser_can_create_role(api_client, superuser):
    api_client.force_authenticate(user=superuser)
    response = api_client.post('/api/roles/', {'name': 'Editor', 'description': '', 'permission_ids': []})
    assert response.status_code == 201


def test_regular_user_cannot_create_role(api_client, regular_user):
    api_client.force_authenticate(user=regular_user)
    response = api_client.post('/api/roles/', {'name': 'Editor'})
    assert response.status_code == 403


def test_user_with_view_perm_can_list_invoices(
    api_client, regular_user, invoice_viewer_role
):
    regular_user.roles.add(invoice_viewer_role)
    api_client.force_authenticate(user=regular_user)
    response = api_client.get('/api/invoices/')
    assert response.status_code == 200


def test_user_without_perm_cannot_delete(api_client, regular_user, invoice_viewer_role):
    regular_user.roles.add(invoice_viewer_role)
    api_client.force_authenticate(user=regular_user)
    # Create an invoice first
    invoice = Invoice.objects.create(number='INV-001', amount=100)
    response = api_client.delete(f'/api/invoices/{invoice.pk}/')
    assert response.status_code == 403


def test_no_privilege_escalation(api_client, superuser, regular_user, invoice_viewer_role):
    """A user cannot assign a role containing permissions they lack."""
    regular_user.roles.add(invoice_viewer_role)
    api_client.force_authenticate(user=regular_user)

    # Try to assign a role with delete permission they don't have
    delete_perm = Permission.objects.create(
        codename='invoices.delete', name='Delete Invoices',
        module='invoices', action='delete'
    )
    admin_role = Role.objects.create(name='Invoice Admin')
    admin_role.permissions.add(delete_perm)

    response = api_client.post(f'/api/users/{regular_user.pk}/roles/',
                               {'role_ids': [admin_role.pk]},
                               format='json')
    assert response.status_code == 403


def test_audit_log_created_on_role_creation(db, superuser):
    from roles.models import AuditLog
    Role.objects.create(name='Audited Role', created_by=superuser)
    assert AuditLog.objects.filter(action='role_created').exists()
