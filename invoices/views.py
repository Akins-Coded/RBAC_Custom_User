from rest_framework import viewsets
from roles.permissions import HasRBACPermission
from .models import Invoice
from .serializers import InvoiceSerializer


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    Manage invoices with RBAC protection.
    Permissions required:
    - List/Retrieve: invoices.view
    - Create: invoices.create
    - Update: invoices.edit
    - Delete: invoices.delete
    """
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [HasRBACPermission]

    ACTION_PERMISSIONS = {
        'list':    'invoices.view',
        'retrieve':'invoices.view',
        'create':  'invoices.create',
        'update':  'invoices.edit',
        'partial_update': 'invoices.edit',
        'destroy': 'invoices.delete',
    }

    def get_permissions(self):
        self.required_permission = self.ACTION_PERMISSIONS.get(self.action, '')
        return super().get_permissions()
