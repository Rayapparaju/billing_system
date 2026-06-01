from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='list'),
    path('add/', views.product_add, name='add'),
    path('edit/<int:pk>/', views.product_edit, name='edit'),
    path('delete/<int:pk>/', views.product_delete, name='delete'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/delete/<int:pk>/', views.category_delete, name='category_delete'),
]
