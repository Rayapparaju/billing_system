from django.contrib import admin
from .models import PurchaseInvoice, PurchaseItem

admin.site.register(PurchaseInvoice)
admin.site.register(PurchaseItem)
