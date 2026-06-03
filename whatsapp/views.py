from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from sales.models import SaleInvoice, SaleItem, Receipt
from purchases.models import PurchaseInvoice, PurchaseItem, Payment
from accounts.models import Company
from .utils import send_whatsapp, build_invoice_message, build_purchase_message, build_receipt_message, build_payment_message

def get_company(request):
    if hasattr(request.user, 'company'):
        return request.user.company
    return None

@login_required
def send_sale_invoice(request, pk):
    invoice = get_object_or_404(SaleInvoice.objects.select_related('customer'), pk=pk)
    items = SaleItem.objects.filter(invoice=invoice).select_related('product')
    company = get_company(request)
    phone = invoice.customer.phone
    if not phone:
        messages.error(request, 'Customer has no phone number.')
        return redirect('sales:detail', pk=pk)
    if request.method == 'POST':
        msg = build_invoice_message(invoice, items, company)
        success, result = send_whatsapp(phone, msg)
        if success:
            messages.success(request, f'Invoice sent via WhatsApp to {invoice.customer.name}.')
        else:
            messages.error(request, f'WhatsApp send failed: {result}')
        return redirect('sales:detail', pk=pk)
    msg_preview = build_invoice_message(invoice, items, company)
    return render(request, 'whatsapp/confirm.html', {
        'title': f'Send Invoice {invoice.invoice_no}',
        'phone': phone,
        'message': msg_preview,
        'cancel_url': reverse('sales:detail', args=[pk]),
    })

@login_required
def send_purchase_invoice(request, pk):
    invoice = get_object_or_404(PurchaseInvoice.objects.select_related('supplier'), pk=pk)
    items = PurchaseItem.objects.filter(invoice=invoice).select_related('product')
    company = get_company(request)
    phone = invoice.supplier.phone
    if not phone:
        messages.error(request, 'Supplier has no phone number.')
        return redirect('purchases:detail', pk=pk)
    if request.method == 'POST':
        msg = build_purchase_message(invoice, items, company)
        success, result = send_whatsapp(phone, msg)
        if success:
            messages.success(request, f'Purchase sent via WhatsApp to {invoice.supplier.name}.')
        else:
            messages.error(request, f'WhatsApp send failed: {result}')
        return redirect('purchases:detail', pk=pk)
    msg_preview = build_purchase_message(invoice, items, company)
    return render(request, 'whatsapp/confirm.html', {
        'title': f'Send Purchase {invoice.invoice_no}',
        'phone': phone,
        'message': msg_preview,
        'cancel_url': reverse('purchases:detail', args=[pk]),
    })

@login_required
def send_receipt(request, pk):
    receipt = get_object_or_404(Receipt.objects.select_related('customer', 'invoice'), pk=pk)
    company = get_company(request)
    phone = receipt.customer.phone
    if not phone:
        messages.error(request, 'Customer has no phone number.')
        return redirect('sales:receipt_list')
    if request.method == 'POST':
        msg = build_receipt_message(receipt, company)
        success, result = send_whatsapp(phone, msg)
        if success:
            messages.success(request, f'Receipt sent via WhatsApp to {receipt.customer.name}.')
        else:
            messages.error(request, f'WhatsApp send failed: {result}')
        return redirect('sales:receipt_list')
    msg_preview = build_receipt_message(receipt, company)
    return render(request, 'whatsapp/confirm.html', {
        'title': f'Send Receipt {receipt.receipt_no}',
        'phone': phone,
        'message': msg_preview,
        'cancel_url': reverse('sales:receipt_list'),
    })

@login_required
def send_payment(request, pk):
    payment = get_object_or_404(Payment.objects.select_related('supplier', 'invoice'), pk=pk)
    company = get_company(request)
    phone = payment.supplier.phone
    if not phone:
        messages.error(request, 'Supplier has no phone number.')
        return redirect('purchases:payment_list')
    if request.method == 'POST':
        msg = build_payment_message(payment, company)
        success, result = send_whatsapp(phone, msg)
        if success:
            messages.success(request, f'Payment sent via WhatsApp to {payment.supplier.name}.')
        else:
            messages.error(request, f'WhatsApp send failed: {result}')
        return redirect('purchases:payment_list')
    msg_preview = build_payment_message(payment, company)
    return render(request, 'whatsapp/confirm.html', {
        'title': f'Send Payment {payment.payment_no}',
        'phone': phone,
        'message': msg_preview,
        'cancel_url': reverse('purchases:payment_list'),
    })
