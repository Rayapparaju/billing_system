from django.urls import path
from . import views

app_name = 'whatsapp'

urlpatterns = [
    path('sale/<int:pk>/', views.send_sale_invoice, name='send_sale'),
    path('purchase/<int:pk>/', views.send_purchase_invoice, name='send_purchase'),
    path('receipt/<int:pk>/', views.send_receipt, name='send_receipt'),
    path('payment/<int:pk>/', views.send_payment, name='send_payment'),
]
