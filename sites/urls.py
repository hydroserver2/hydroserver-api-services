from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('', views.sites, name="sites"),
    path('register-site/', views.register_site, name="register-site"),
    path('delete-site/<str:pk>', views.delete_site, name="delete-site"),
    path('update_follow/<path:pk>/', views.update_follow, name='update_follow'),
    path('browse/', views.browse_sites, name='browse'),
    path('export_csv/<str:thing_pk>/', views.export_csv, name='export_csv'),
]
