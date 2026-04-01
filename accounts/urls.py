from django.urls import path
from . import views

urlpatterns = [
    path('users/<int:user_id>/roles/', views.assign_roles, name='assign-roles'),
]
