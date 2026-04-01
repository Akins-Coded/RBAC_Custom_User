from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from roles.views import RoleViewSet, PermissionViewSet
from invoices.views import InvoiceViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'roles',       RoleViewSet,       basename='role')
router.register(r'permissions', PermissionViewSet, basename='permission')
router.register(r'invoices',    InvoiceViewSet,    basename='invoice')

urlpatterns = [
    path('admin/',    admin.site.urls),
    path('api/',      include(router.urls)),
    path('api/',      include('accounts.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
