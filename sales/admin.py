from django.contrib import admin
from .models import SaleInvoice, SaleItem

admin.site.register(SaleInvoice)
admin.site.register(SaleItem)
