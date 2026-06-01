from django.contrib import admin
from .models import SaleInvoice, SaleItem, SalesReturn, SalesReturnItem

admin.site.register(SaleInvoice)
admin.site.register(SaleItem)
admin.site.register(SalesReturn)
admin.site.register(SalesReturnItem)
