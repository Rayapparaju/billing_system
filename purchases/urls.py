from django.urls import path
from . import views

app_name = 'purchases'

urlpatterns = [
    path('', views.purchase_list, name='list'),
    path('create/', views.purchase_create, name='create'),
    path('<int:pk>/', views.purchase_detail, name='detail'),
    path('<int:pk>/delete/', views.purchase_delete, name='delete'),
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/create/', views.payment_create, name='payment_create'),
    path('payments/<int:pk>/delete/', views.payment_delete, name='payment_delete'),
    path('returns/', views.purchase_return_list, name='return_list'),
    path('returns/create/', views.purchase_return_create, name='return_create'),
    path('returns/<int:pk>/', views.purchase_return_detail, name='return_detail'),
]
