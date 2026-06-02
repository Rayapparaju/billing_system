import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import PurchaseInvoice, PurchaseItem, Payment, PurchaseReturn, PurchaseReturnItem
from suppliers.models import Supplier
from products.models import Product


def update_purchase_payment_status(invoice):
    total_paid = Payment.objects.filter(invoice=invoice).aggregate(Sum('amount'))['amount__sum'] or 0
    if total_paid >= invoice.grand_total:
        invoice.payment_status = 'Paid'
    elif total_paid > 0:
        invoice.payment_status = 'Partial'
    else:
        invoice.payment_status = 'Unpaid'
    invoice.save(update_fields=['payment_status'])

@login_required
def purchase_list(request):
    invoices = PurchaseInvoice.objects.select_related('supplier').all().order_by('-created_date')
    return render(request, 'purchases/purchase_list.html', {'invoices': invoices})

@login_required
def purchase_create(request):
    suppliers = Supplier.objects.all()
    products = Product.objects.all()
    if request.method == 'POST':
        supplier_id = request.POST.get('supplier')
        payment_status = request.POST.get('payment_status', 'Unpaid')
        items_data = json.loads(request.POST.get('items', '[]'))
        if not supplier_id:
            messages.error(request, 'Please select a supplier.')
            return redirect('purchases:create')
        if not items_data:
            messages.error(request, 'Please add at least one item.')
            return redirect('purchases:create')
        supplier = get_object_or_404(Supplier, pk=supplier_id)
        last_invoice = PurchaseInvoice.objects.order_by('-id').first()
        last_num = 0
        if last_invoice and last_invoice.invoice_no.startswith('PINV-'):
            try:
                last_num = int(last_invoice.invoice_no.replace('PINV-', ''))
            except:
                pass
        invoice_no = f'PINV-{str(last_num + 1).zfill(5)}'
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
        invoice = PurchaseInvoice.objects.create(
            invoice_no=invoice_no,
            supplier=supplier,
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
            PurchaseItem.objects.create(
                invoice=invoice,
                product=product,
                quantity=qty,
                rate=rate,
                gst=gst_pct,
                discount=discount_amt,
                total=line_total,
            )
            product.stock_quantity += qty
            product.save()
        messages.success(request, f'Purchase invoice {invoice_no} created successfully.')
        return redirect('purchases:list')
    context = {'suppliers': suppliers, 'products': products}
    return render(request, 'purchases/purchase_form.html', context)

@login_required
def purchase_detail(request, pk):
    invoice = get_object_or_404(PurchaseInvoice.objects.select_related('supplier'), pk=pk)
    items = PurchaseItem.objects.filter(invoice=invoice).select_related('product')
    payments = Payment.objects.filter(invoice=invoice).order_by('-created_date')
    total_paid = sum(p.amount for p in payments)
    balance = invoice.grand_total - total_paid
    return render(request, 'purchases/purchase_detail.html', {
        'invoice': invoice, 'items': items,
        'payments': payments, 'total_paid': total_paid, 'balance': balance,
    })

@login_required
def payment_list(request):
    payments = Payment.objects.select_related('supplier', 'invoice').all().order_by('-created_date')
    invoice_ids = [p.invoice_id for p in payments if p.invoice_id]
    totals_paid = PurchaseInvoice.objects.filter(id__in=invoice_ids).annotate(
        total_paid=Sum('payments__amount')
    ).values_list('id', 'grand_total', 'total_paid')
    balance_map = {}
    for iid, gt, tp in totals_paid:
        balance_map[iid] = float(gt) - float(tp or 0)
    return render(request, 'purchases/payment_list.html', {
        'payments': payments,
        'balance_map': balance_map,
    })

@login_required
def payment_create(request):
    suppliers = Supplier.objects.all()
    if request.method == 'POST':
        supplier_id = request.POST.get('supplier')
        invoice_id = request.POST.get('invoice')
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method', 'Cash')
        reference_no = request.POST.get('reference_no', '')
        notes = request.POST.get('notes', '')
        if not supplier_id or not amount:
            messages.error(request, 'Supplier and amount are required.')
            return redirect('purchases:payment_create')
        try:
            amount = float(amount)
        except:
            messages.error(request, 'Invalid amount.')
            return redirect('purchases:payment_create')
        supplier = get_object_or_404(Supplier, pk=supplier_id)
        invoice = None
        if invoice_id:
            invoice = get_object_or_404(PurchaseInvoice, pk=invoice_id)
        last_pmt = Payment.objects.order_by('-id').first()
        last_num = 0
        if last_pmt and last_pmt.payment_no.startswith('PAY-'):
            try:
                last_num = int(last_pmt.payment_no.replace('PAY-', ''))
            except:
                pass
        payment_no = f'PAY-{str(last_num + 1).zfill(5)}'
        Payment.objects.create(
            payment_no=payment_no, supplier=supplier, invoice=invoice,
            amount=amount, payment_method=payment_method,
            reference_no=reference_no, notes=notes,
        )
        if invoice:
            update_purchase_payment_status(invoice)
        messages.success(request, f'Payment {payment_no} recorded successfully.')
        return redirect('purchases:payment_list')
    invoices = PurchaseInvoice.objects.select_related('supplier').all().order_by('-created_date')
    preselected_invoice = request.GET.get('invoice')
    return render(request, 'purchases/payment_form.html', {
        'suppliers': suppliers, 'invoices': invoices,
        'preselected_invoice': preselected_invoice,
    })

@login_required
def payment_delete(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        invoice = payment.invoice
        payment.delete()
        if invoice:
            update_purchase_payment_status(invoice)
        messages.success(request, 'Payment deleted.')
        return redirect('purchases:payment_list')
    return render(request, 'purchases/payment_confirm_delete.html', {'payment': payment})

@login_required
def purchase_delete(request, pk):
    invoice = get_object_or_404(PurchaseInvoice, pk=pk)
    if request.method == 'POST':
        items = PurchaseItem.objects.filter(invoice=invoice)
        for item in items:
            product = item.product
            product.stock_quantity -= item.quantity
            product.save()
        invoice.delete()
        messages.success(request, 'Purchase invoice deleted successfully.')
        return redirect('purchases:list')
    return render(request, 'purchases/purchase_confirm_delete.html', {'invoice': invoice})

@login_required
def purchase_return_list(request):
    returns = PurchaseReturn.objects.select_related('supplier', 'purchase_invoice').all().order_by('-created_date')
    return render(request, 'purchases/purchase_return_list.html', {'returns': returns})

@login_required
def purchase_return_create(request):
    invoices = PurchaseInvoice.objects.select_related('supplier').all().order_by('-created_date')
    products = Product.objects.all()
    if request.method == 'POST':
        invoice_id = request.POST.get('invoice')
        reason = request.POST.get('reason', '')
        items_data = json.loads(request.POST.get('items', '[]'))
        if not invoice_id or not items_data:
            messages.error(request, 'Please select an invoice and add items.')
            return redirect('purchases:return_create')
        purchase_invoice = get_object_or_404(PurchaseInvoice, pk=invoice_id)
        supplier = purchase_invoice.supplier
        last_return = PurchaseReturn.objects.order_by('-id').first()
        last_num = 0
        if last_return and last_return.return_no.startswith('PRET-'):
            try:
                last_num = int(last_return.return_no.replace('PRET-', ''))
            except:
                pass
        return_no = f'PRET-{str(last_num + 1).zfill(5)}'
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
        return_inv = PurchaseReturn.objects.create(
            return_no=return_no, purchase_invoice=purchase_invoice, supplier=supplier,
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
            PurchaseReturnItem.objects.create(
                return_invoice=return_inv, product=product, quantity=qty,
                rate=rate, gst=gst_pct, discount=discount_amt, total=line_total,
            )
            product.stock_quantity -= qty
            product.save()
        messages.success(request, f'Purchase return {return_no} created successfully.')
        return redirect('purchases:return_list')
    return render(request, 'purchases/purchase_return_form.html', {'invoices': invoices, 'products': products})

@login_required
def purchase_return_detail(request, pk):
    return_inv = get_object_or_404(PurchaseReturn.objects.select_related('supplier', 'purchase_invoice'), pk=pk)
    items = PurchaseReturnItem.objects.filter(return_invoice=return_inv).select_related('product')
    return render(request, 'purchases/purchase_return_detail.html', {'return_inv': return_inv, 'items': items})
