from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('', views.customer_list, name='list'),
    path('add/', views.customer_add, name='add'),
    path('edit/<int:pk>/', views.customer_edit, name='edit'),
    path('delete/<int:pk>/', views.customer_delete, name='delete'),
]
