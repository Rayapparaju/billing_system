import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from .models import SaleInvoice, SaleItem, Receipt, SalesReturn, SalesReturnItem
from customers.models import Customer
from products.models import Product

def update_invoice_payment_status(invoice):
    total_paid = Receipt.objects.filter(invoice=invoice).aggregate(Sum('amount'))['amount__sum'] or 0
    if total_paid >= invoice.grand_total:
        invoice.payment_status = 'Paid'
    elif total_paid > 0:
        invoice.payment_status = 'Partial'
    else:
        invoice.payment_status = 'Unpaid'
    invoice.save(update_fields=['payment_status'])

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
    receipts = Receipt.objects.filter(invoice=invoice).order_by('-created_date')
    total_paid = sum(r.amount for r in receipts)
    balance = invoice.grand_total - total_paid
    return render(request, 'sales/sale_detail.html', {
        'invoice': invoice, 'items': items,
        'receipts': receipts, 'total_paid': total_paid, 'balance': balance,
    })

@login_required
def sale_print(request, pk):
    invoice = get_object_or_404(SaleInvoice.objects.select_related('customer'), pk=pk)
    items = SaleItem.objects.filter(invoice=invoice).select_related('product')
    company = None
    if hasattr(request.user, 'company'):
        company = request.user.company
    return render(request, 'sales/sale_print.html', {'invoice': invoice, 'items': items, 'company': company})

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

@login_required
def receipt_list(request):
    receipts = Receipt.objects.select_related('customer', 'invoice').all().order_by('-created_date')
    invoice_ids = [r.invoice_id for r in receipts if r.invoice_id]
    totals_paid = SaleInvoice.objects.filter(id__in=invoice_ids).annotate(
        total_paid=Sum('receipts__amount')
    ).values_list('id', 'grand_total', 'total_paid')
    balance_map = {}
    for iid, gt, tp in totals_paid:
        balance_map[iid] = float(gt) - float(tp or 0)
    return render(request, 'sales/receipt_list.html', {
        'receipts': receipts,
        'balance_map': balance_map,
    })

@login_required
def receipt_create(request):
    customers = Customer.objects.all()
    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        invoice_id = request.POST.get('invoice')
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method', 'Cash')
        reference_no = request.POST.get('reference_no', '')
        notes = request.POST.get('notes', '')
        if not customer_id or not amount:
            messages.error(request, 'Customer and amount are required.')
            return redirect('sales:receipt_create')
        try:
            amount = float(amount)
        except:
            messages.error(request, 'Invalid amount.')
            return redirect('sales:receipt_create')
        customer = get_object_or_404(Customer, pk=customer_id)
        invoice = None
        if invoice_id:
            invoice = get_object_or_404(SaleInvoice, pk=invoice_id)
        last_rcpt = Receipt.objects.order_by('-id').first()
        last_num = 0
        if last_rcpt and last_rcpt.receipt_no.startswith('RCPT-'):
            try:
                last_num = int(last_rcpt.receipt_no.replace('RCPT-', ''))
            except:
                pass
        receipt_no = f'RCPT-{str(last_num + 1).zfill(5)}'
        receipt = Receipt.objects.create(
            receipt_no=receipt_no, customer=customer, invoice=invoice,
            amount=amount, payment_method=payment_method,
            reference_no=reference_no, notes=notes,
        )
        if invoice:
            update_invoice_payment_status(invoice)
        messages.success(request, f'Receipt {receipt_no} recorded successfully.')
        return redirect('sales:receipt_list')
    invoices = SaleInvoice.objects.select_related('customer').all().order_by('-created_date')
    preselected_invoice = request.GET.get('invoice')
    return render(request, 'sales/receipt_form.html', {
        'customers': customers, 'invoices': invoices,
        'preselected_invoice': preselected_invoice,
    })

@login_required
def receipt_delete(request, pk):
    receipt = get_object_or_404(Receipt, pk=pk)
    if request.method == 'POST':
        invoice = receipt.invoice
        receipt.delete()
        if invoice:
            update_invoice_payment_status(invoice)
        messages.success(request, 'Receipt deleted.')
        return redirect('sales:receipt_list')
    return render(request, 'sales/receipt_confirm_delete.html', {'receipt': receipt})

@login_required
def sales_return_list(request):
    returns = SalesReturn.objects.select_related('customer', 'sale_invoice').all().order_by('-created_date')
    return render(request, 'sales/sales_return_list.html', {'returns': returns})

@login_required
def sales_return_create(request):
    invoices = SaleInvoice.objects.select_related('customer').all().order_by('-created_date')
    products = Product.objects.all()
    if request.method == 'POST':
        invoice_id = request.POST.get('invoice')
        reason = request.POST.get('reason', '')
        items_data = json.loads(request.POST.get('items', '[]'))
        if not invoice_id or not items_data:
            messages.error(request, 'Please select an invoice and add items.')
            return redirect('sales:return_create')
        sale_invoice = get_object_or_404(SaleInvoice, pk=invoice_id)
        customer = sale_invoice.customer
        last_return = SalesReturn.objects.order_by('-id').first()
        last_num = 0
        if last_return and last_return.return_no.startswith('SRET-'):
            try:
                last_num = int(last_return.return_no.replace('SRET-', ''))
            except:
                pass
        return_no = f'SRET-{str(last_num + 1).zfill(5)}'
        subtotal = total_gst = total_discount = 0.0
        for item in items_data:
            product = get_object_or_404(Product, pk=item['product_id'])
            qty = int(item['quantity'])
            rate = float(item['rate'])
            gst_pct = float(item.get('gst', 0))
            disc = float(item.get('discount', 0))
            item_total = qty * rate
            gst_amt = item_total * (gst_pct / 100)
            discount_amt = item_total * (disc / 100) if disc > 0 else disc
            subtotal += item_total
            total_gst += gst_amt
            total_discount += discount_amt
        grand_total = subtotal + total_gst - total_discount
        return_inv = SalesReturn.objects.create(
            return_no=return_no, sale_invoice=sale_invoice, customer=customer,
            subtotal=subtotal, discount=total_discount, gst_amount=total_gst,
            grand_total=grand_total, reason=reason,
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
            SalesReturnItem.objects.create(
                return_invoice=return_inv, product=product, quantity=qty,
                rate=rate, gst=gst_pct, discount=discount_amt, total=line_total,
            )
            product.stock_quantity += qty
            product.save()
        messages.success(request, f'Sales return {return_no} created successfully.')
        return redirect('sales:return_list')
    return render(request, 'sales/sales_return_form.html', {'invoices': invoices, 'products': products})

@login_required
def sales_return_detail(request, pk):
    return_inv = get_object_or_404(SalesReturn.objects.select_related('customer', 'sale_invoice'), pk=pk)
    items = SalesReturnItem.objects.filter(return_invoice=return_inv).select_related('product')
    return render(request, 'sales/sales_return_detail.html', {'return_inv': return_inv, 'items': items})
