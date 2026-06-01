from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('daily-sales/', views.daily_sales, name='daily_sales'),
    path('monthly-sales/', views.monthly_sales, name='monthly_sales'),
    path('purchases/', views.purchase_report, name='purchase_report'),
    path('stock/', views.stock_report, name='stock_report'),
    path('low-stock/', views.low_stock_report, name='low_stock_report'),
    path('customer-ledger/', views.customer_ledger, name='customer_ledger'),
    path('supplier-ledger/', views.supplier_ledger, name='supplier_ledger'),
    path('profit-loss/', views.profit_loss, name='profit_loss'),
    path('debtors/', views.debtors, name='debtors'),
    path('creditors/', views.creditors, name='creditors'),
]
