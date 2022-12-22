from django.urls import path
from sites import views

urlpatterns = [
    path('', views.sites, name="sites"),
    path('sites/<str:pk>/', views.site, name="site"),
    path('add-site/', views.add_site, name="add-site"),
    path('delete-site/<str:pk>', views.delete_site, name="delete-site"),
]
