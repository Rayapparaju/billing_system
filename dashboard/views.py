from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from django.db.models.functions import TruncMonth
from customers.models import Customer
from suppliers.models import Supplier
from products.models import Product
from sales.models import SaleInvoice
from purchases.models import PurchaseInvoice

@login_required
def dashboard_home(request):
    total_sales = SaleInvoice.objects.aggregate(Sum('grand_total'))['grand_total__sum'] or 0
    total_purchases = PurchaseInvoice.objects.aggregate(Sum('grand_total'))['grand_total__sum'] or 0
    total_customers = Customer.objects.count()
    total_suppliers = Supplier.objects.count()
    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(stock_quantity__lte=F('low_stock_alert_qty')).count()
    recent_invoices = SaleInvoice.objects.select_related('customer').order_by('-created_date')[:5]

    sales_chart = (
        SaleInvoice.objects.annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('grand_total'))
        .order_by('month')
    )
    sales_labels = [s['month'].strftime('%b %Y') if s['month'] else '' for s in sales_chart]
    sales_data = [float(s['total']) for s in sales_chart]

    context = {
        'total_sales': total_sales,
        'total_purchases': total_purchases,
        'total_customers': total_customers,
        'total_suppliers': total_suppliers,
        'total_products': total_products,
        'low_stock_products': low_stock_products,
        'recent_invoices': recent_invoices,
        'sales_labels': sales_labels,
        'sales_data': sales_data,
    }
    return render(request, 'dashboard/home.html', context)
