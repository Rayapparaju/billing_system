from django.contrib import admin
from .models import PurchaseInvoice, PurchaseItem, PurchaseReturn, PurchaseReturnItem

admin.site.register(PurchaseInvoice)
admin.site.register(PurchaseItem)
admin.site.register(PurchaseReturn)
admin.site.register(PurchaseReturnItem)
