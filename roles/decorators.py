from functools import wraps
from django.http import JsonResponse


def rbac_required(codename):
    """
    Usage:
        @rbac_required('invoices.delete')
        def delete_invoice(request, pk):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({'detail': 'Authentication required.'}, status=401)
            if not request.user.has_rbac_perm(codename):
                return JsonResponse({'detail': 'Permission denied.'}, status=403)
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
