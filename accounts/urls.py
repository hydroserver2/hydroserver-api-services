from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('update-account/', views.update_account, name='update_account'),
    path('remove-account/', views.remove_account, name='remove_account'),
]
