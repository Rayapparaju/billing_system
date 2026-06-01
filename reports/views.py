from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from datetime import datetime
from customers.models import Customer
from suppliers.models import Supplier
from products.models import Product
from sales.models import SaleInvoice
from purchases.models import PurchaseInvoice

@login_required
def daily_sales(request):
    today = datetime.now().date()
    invoices = SaleInvoice.objects.filter(date=today).select_related('customer').order_by('-created_date')
    total = invoices.aggregate(Sum('grand_total'))['grand_total__sum'] or 0
    return render(request, 'reports/daily_sales.html', {'invoices': invoices, 'total': total, 'today': today})

@login_required
def monthly_sales(request):
    month = request.GET.get('month', datetime.now().strftime('%Y-%m'))
    year, m = month.split('-')
    invoices = SaleInvoice.objects.filter(date__year=year, date__month=m).select_related('customer').order_by('-created_date')
    total = invoices.aggregate(Sum('grand_total'))['grand_total__sum'] or 0
    return render(request, 'reports/monthly_sales.html', {'invoices': invoices, 'total': total, 'month': month})

@login_required
def purchase_report(request):
    month = request.GET.get('month', datetime.now().strftime('%Y-%m'))
    year, m = month.split('-')
    invoices = PurchaseInvoice.objects.filter(date__year=year, date__month=m).select_related('supplier').order_by('-created_date')
    total = invoices.aggregate(Sum('grand_total'))['grand_total__sum'] or 0
    return render(request, 'reports/purchase_report.html', {'invoices': invoices, 'total': total, 'month': month})

@login_required
def stock_report(request):
    products = Product.objects.select_related('category').all().order_by('name')
    return render(request, 'reports/stock_report.html', {'products': products})

@login_required
def low_stock_report(request):
    products = Product.objects.filter(stock_quantity__lte=F('low_stock_alert_qty')).order_by('stock_quantity')
    return render(request, 'reports/low_stock_report.html', {'products': products})

@login_required
def customer_ledger(request):
    customer_id = request.GET.get('customer')
    customer = None
    sales = None
    if customer_id:
        customer = Customer.objects.get(pk=customer_id)
        sales = SaleInvoice.objects.filter(customer=customer).order_by('-created_date')
    customers = Customer.objects.all()
    return render(request, 'reports/customer_ledger.html', {'customers': customers, 'customer': customer, 'sales': sales})

@login_required
def supplier_ledger(request):
    supplier_id = request.GET.get('supplier')
    supplier = None
    purchases = None
    if supplier_id:
        supplier = Supplier.objects.get(pk=supplier_id)
        purchases = PurchaseInvoice.objects.filter(supplier=supplier).order_by('-created_date')
    suppliers = Supplier.objects.all()
    return render(request, 'reports/supplier_ledger.html', {'suppliers': suppliers, 'supplier': supplier, 'purchases': purchases})

@login_required
def profit_loss(request):
    total_sales = SaleInvoice.objects.aggregate(Sum('grand_total'))['grand_total__sum'] or 0
    total_purchases = PurchaseInvoice.objects.aggregate(Sum('grand_total'))['grand_total__sum'] or 0
    profit = total_sales - total_purchases
    return render(request, 'reports/profit_loss.html', {'total_sales': total_sales, 'total_purchases': total_purchases, 'profit': profit})

@login_required
def debtors(request):
    debtors_data = []
    customers = Customer.objects.all()
    for c in customers:
        unpaid = SaleInvoice.objects.filter(customer=c, payment_status='Unpaid').aggregate(Sum('grand_total'))['grand_total__sum'] or 0
        partial = SaleInvoice.objects.filter(customer=c, payment_status='Partial').aggregate(Sum('grand_total'))['grand_total__sum'] or 0
        total_due = unpaid + partial
        if total_due > 0:
            debtors_data.append({'customer': c, 'total_due': total_due})
    return render(request, 'reports/debtors.html', {'debtors': debtors_data})

@login_required
def creditors(request):
    creditors_data = []
    suppliers = Supplier.objects.all()
    for s in suppliers:
        unpaid = PurchaseInvoice.objects.filter(supplier=s, payment_status='Unpaid').aggregate(Sum('grand_total'))['grand_total__sum'] or 0
        partial = PurchaseInvoice.objects.filter(supplier=s, payment_status='Partial').aggregate(Sum('grand_total'))['grand_total__sum'] or 0
        total_due = unpaid + partial
        if total_due > 0:
            creditors_data.append({'supplier': s, 'total_due': total_due})
    return render(request, 'reports/creditors.html', {'creditors': creditors_data})
