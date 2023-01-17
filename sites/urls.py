from django.urls import path
from . import views

urlpatterns = [
    path('', views.sites, name="sites"),
    path('sites/<str:pk>/', views.site, name="site"),
    path('register-site/', views.register_site, name="register-site"),
    path('delete-site/<str:pk>', views.delete_site, name="delete-site"),
]
