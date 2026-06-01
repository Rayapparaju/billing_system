from django.db import models
from customers.models import Customer
from products.models import Product

class SaleInvoice(models.Model):
    PAYMENT_CHOICES = [
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
        ('Partial', 'Partial'),
    ]
    invoice_no = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='Unpaid')
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.invoice_no

    class Meta:
        ordering = ['-created_date']

class SaleItem(models.Model):
    invoice = models.ForeignKey(SaleInvoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    rate = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    gst = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.product.name} - {self.invoice.invoice_no}"
