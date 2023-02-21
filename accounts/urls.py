from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('update-account/', views.update_account, name='update_account'),
    path('remove-account/', views.remove_account, name='remove_account'),
    path('create-organization/', views.create_organization, name='create_organization'),
    path('update-organization/<str:pk>/', views.update_organization, name='update_organization'),
    path('delete-organization/<str:pk>/', views.delete_organization, name='delete_organization'),
    path('add-organization-admin/<str:pk>/', views.add_organization_admin, name='add_organization_admin'),
]
