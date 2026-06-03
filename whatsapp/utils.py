from twilio.rest import Client
from django.conf import settings

def format_phone(phone):
    if not phone:
        return ''
    phone = phone.strip().replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    if phone.startswith('+'):
        return phone
    if phone.startswith('0'):
        return '+91' + phone[1:]
    if len(phone) == 10:
        return '+91' + phone
    return '+91' + phone

def send_whatsapp(to, message):
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        return False, 'Twilio not configured. Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN.'
    to_whatsapp = f'whatsapp:{format_phone(to)}'
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=settings.TWILIO_WHATSAPP_FROM,
            to=to_whatsapp,
        )
        return True, 'Message sent successfully.'
    except Exception as e:
        return False, str(e)

def build_invoice_message(invoice, items, company=None):
    lines = []
    lines.append(f'*INVOICE: {invoice.invoice_no}*')
    lines.append(f'Date: {invoice.date}')
    lines.append(f'Customer: {invoice.customer.name}')
    if company:
        lines.append(f'From: {company.name}')
    lines.append('')
    lines.append('_' + '-'*30 + '_')
    for item in items:
        lines.append(f'{item.product.name} x{item.quantity} @ {item.rate} = \u20b9{item.total:.2f}')
    lines.append('_' + '-'*30 + '_')
    lines.append(f'Subtotal: \u20b9{invoice.subtotal:.2f}')
    if invoice.discount:
        lines.append(f'Discount: -\u20b9{invoice.discount:.2f}')
    if invoice.gst_amount:
        lines.append(f'GST: \u20b9{invoice.gst_amount:.2f}')
    lines.append(f'*Total: \u20b9{invoice.grand_total:.2f}*')
    lines.append(f'Status: {invoice.payment_status}')
    return '\n'.join(lines)

def build_purchase_message(invoice, items, company=None):
    lines = []
    lines.append(f'*PURCHASE: {invoice.invoice_no}*')
    lines.append(f'Date: {invoice.date}')
    lines.append(f'Supplier: {invoice.supplier.name}')
    if company:
        lines.append(f'From: {company.name}')
    lines.append('')
    lines.append('_' + '-'*30 + '_')
    for item in items:
        lines.append(f'{item.product.name} x{item.quantity} @ {item.rate} = \u20b9{item.total:.2f}')
    lines.append('_' + '-'*30 + '_')
    lines.append(f'Subtotal: \u20b9{invoice.subtotal:.2f}')
    if invoice.discount:
        lines.append(f'Discount: -\u20b9{invoice.discount:.2f}')
    if invoice.gst_amount:
        lines.append(f'GST: \u20b9{invoice.gst_amount:.2f}')
    lines.append(f'*Total: \u20b9{invoice.grand_total:.2f}*')
    lines.append(f'Status: {invoice.payment_status}')
    return '\n'.join(lines)

def build_receipt_message(receipt, company=None):
    lines = []
    lines.append(f'*PAYMENT RECEIPT: {receipt.receipt_no}*')
    lines.append(f'Date: {receipt.date}')
    lines.append(f'Customer: {receipt.customer.name}')
    if receipt.invoice:
        lines.append(f'Invoice: {receipt.invoice.invoice_no}')
    lines.append('')
    lines.append(f'Amount Received: \u20b9{receipt.amount:.2f}')
    lines.append(f'Method: {receipt.payment_method}')
    if receipt.reference_no:
        lines.append(f'Ref: {receipt.reference_no}')
    if company:
        lines.append(f'From: {company.name}')
    return '\n'.join(lines)

def build_payment_message(payment, company=None):
    lines = []
    lines.append(f'*PAYMENT SENT: {payment.payment_no}*')
    lines.append(f'Date: {payment.date}')
    lines.append(f'Supplier: {payment.supplier.name}')
    if payment.invoice:
        lines.append(f'Invoice: {payment.invoice.invoice_no}')
    lines.append('')
    lines.append(f'Amount Paid: \u20b9{payment.amount:.2f}')
    lines.append(f'Method: {payment.payment_method}')
    if payment.reference_no:
        lines.append(f'Ref: {payment.reference_no}')
    if company:
        lines.append(f'From: {company.name}')
    return '\n'.join(lines)
