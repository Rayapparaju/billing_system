from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.sale_list, name='list'),
    path('create/', views.sale_create, name='create'),
    path('<int:pk>/', views.sale_detail, name='detail'),
    path('<int:pk>/print/', views.sale_print, name='print'),
    path('<int:pk>/delete/', views.sale_delete, name='delete'),
    path('receipts/', views.receipt_list, name='receipt_list'),
    path('receipts/create/', views.receipt_create, name='receipt_create'),
    path('receipts/<int:pk>/delete/', views.receipt_delete, name='receipt_delete'),
    path('returns/', views.sales_return_list, name='return_list'),
    path('returns/create/', views.sales_return_create, name='return_create'),
    path('returns/<int:pk>/', views.sales_return_detail, name='return_detail'),
]
