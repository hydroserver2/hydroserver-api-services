from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('', views.sites, name="sites"),
    path('register-site/', views.register_site, name="register-site"),
    path('update-site/<str:pk>', views.update_site, name="update_site"),
    path('delete-site/<str:pk>', views.delete_site, name="delete-site"),
    path('add-owner/<str:pk>', views.add_owner, name="add_owner"),
    path('update_follow/<path:pk>/', views.update_follow, name='update_follow'),
    path('browse/', views.browse_sites, name='browse'),
    path('add_sensor/', views.add_sensor, name='add_sensor'),
    path('datastream/<str:pk>/', views.datastream, name='datastream'),
    path('register-datastream/<str:pk>/', views.register_datastream, name='register_datastream'),
    path('update_datastream/<str:datastream_pk>/', views.update_datastream, name='update_datastream'),
    path('remove_datastream/<str:datastream_pk>', views.remove_datastream, name='remove_datastream'),
    path('upload_csv/<str:pk>/', views.upload_csv, name='upload_csv'),
    path('export_csv/<str:thing_pk>/', views.export_csv, name='export_csv'),
]
