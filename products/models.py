from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    hsn_code = models.CharField(max_length=20, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    stock_quantity = models.IntegerField(default=0)
    low_stock_alert_qty = models.IntegerField(default=5)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_date']
