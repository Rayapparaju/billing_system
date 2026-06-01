import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import SaleInvoice, SaleItem
from customers.models import Customer
from products.models import Product

@login_required
def sale_list(request):
    invoices = SaleInvoice.objects.select_related('customer').all().order_by('-created_date')
    return render(request, 'sales/sale_list.html', {'invoices': invoices})

@login_required
def sale_create(request):
    customers = Customer.objects.all()
    products = Product.objects.filter(stock_quantity__gt=0)
    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        payment_status = request.POST.get('payment_status', 'Unpaid')
        items_data = json.loads(request.POST.get('items', '[]'))
        if not customer_id:
            messages.error(request, 'Please select a customer.')
            return redirect('sales:create')
        if not items_data:
            messages.error(request, 'Please add at least one item.')
            return redirect('sales:create')
        customer = get_object_or_404(Customer, pk=customer_id)
        last_invoice = SaleInvoice.objects.order_by('-id').first()
        last_num = 0
        if last_invoice and last_invoice.invoice_no.startswith('SINV-'):
            try:
                last_num = int(last_invoice.invoice_no.replace('SINV-', ''))
            except:
                pass
        invoice_no = f'SINV-{str(last_num + 1).zfill(5)}'
        subtotal = 0
        total_gst = 0
        total_discount = 0
        for item in items_data:
            product = get_object_or_404(Product, pk=item['product_id'])
            qty = int(item['quantity'])
            rate = float(item['rate'])
            gst_pct = float(item.get('gst', 0))
            disc = float(item.get('discount', 0))
            item_total = qty * rate
            gst_amt = item_total * (gst_pct / 100)
            discount_amt = item_total * (disc / 100) if disc > 0 else disc
            line_total = item_total + gst_amt - discount_amt
            subtotal += item_total
            total_gst += gst_amt
            total_discount += discount_amt
        grand_total = subtotal + total_gst - total_discount
        invoice = SaleInvoice.objects.create(
            invoice_no=invoice_no,
            customer=customer,
            subtotal=subtotal,
            discount=total_discount,
            gst_amount=total_gst,
            grand_total=grand_total,
            payment_status=payment_status,
        )
        for item in items_data:
            product = get_object_or_404(Product, pk=item['product_id'])
            qty = int(item['quantity'])
            rate = float(item['rate'])
            gst_pct = float(item.get('gst', 0))
            disc = float(item.get('discount', 0))
            item_total = qty * rate
            gst_amt = item_total * (gst_pct / 100)
            discount_amt = item_total * (disc / 100) if disc > 0 else disc
            line_total = item_total + gst_amt - discount_amt
            SaleItem.objects.create(
                invoice=invoice,
                product=product,
                quantity=qty,
                rate=rate,
                gst=gst_pct,
                discount=discount_amt,
                total=line_total,
            )
            product.stock_quantity -= qty
            product.save()
        messages.success(request, f'Invoice {invoice_no} created successfully.')
        return redirect('sales:list')
    context = {'customers': customers, 'products': products}
    return render(request, 'sales/sale_form.html', context)

@login_required
def sale_detail(request, pk):
    invoice = get_object_or_404(SaleInvoice.objects.select_related('customer'), pk=pk)
    items = SaleItem.objects.filter(invoice=invoice).select_related('product')
    return render(request, 'sales/sale_detail.html', {'invoice': invoice, 'items': items})

@login_required
def sale_print(request, pk):
    invoice = get_object_or_404(SaleInvoice.objects.select_related('customer'), pk=pk)
    items = SaleItem.objects.filter(invoice=invoice).select_related('product')
    return render(request, 'sales/sale_print.html', {'invoice': invoice, 'items': items})

@login_required
def sale_delete(request, pk):
    invoice = get_object_or_404(SaleInvoice, pk=pk)
    if request.method == 'POST':
        items = SaleItem.objects.filter(invoice=invoice)
        for item in items:
            product = item.product
            product.stock_quantity += item.quantity
            product.save()
        invoice.delete()
        messages.success(request, 'Invoice deleted successfully.')
        return redirect('sales:list')
    return render(request, 'sales/sale_confirm_delete.html', {'invoice': invoice})
