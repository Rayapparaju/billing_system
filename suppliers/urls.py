from django.urls import path
from . import views

app_name = 'suppliers'

urlpatterns = [
    path('', views.supplier_list, name='list'),
    path('add/', views.supplier_add, name='add'),
    path('edit/<int:pk>/', views.supplier_edit, name='edit'),
    path('delete/<int:pk>/', views.supplier_delete, name='delete'),
]
