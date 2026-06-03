import pandas as pd
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from customers.models import Customer
from suppliers.models import Supplier
from products.models import Product, Category

def safe_str(val):
    if pd.isna(val) or val is None:
        return ''
    return str(val).strip()

def safe_decimal(val):
    if pd.isna(val) or val is None:
        return 0
    try:
        return float(val)
    except:
        return 0

def safe_int(val):
    if pd.isna(val) or val is None:
        return 0
    try:
        return int(float(val))
    except:
        return 0

@login_required
def import_excel(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        if not file.name.endswith(('.xlsx', '.xls')):
            messages.error(request, 'Please upload a .xlsx or .xls file.')
            return redirect('dataimport:import')
        try:
            dfs = pd.read_excel(file, sheet_name=None, engine='openpyxl')
        except Exception as e:
            messages.error(request, f'Error reading file: {e}')
            return redirect('dataimport:import')
        counts = {'customers': 0, 'suppliers': 0, 'products': 0, 'categories': 0}
        errors = []
        # Customers
        if 'Customers' in dfs:
            df = dfs['Customers']
            for _, row in df.iterrows():
                name = safe_str(row.get('Name'))
                if not name:
                    continue
                Customer.objects.get_or_create(
                    name=name,
                    defaults={
                        'phone': safe_str(row.get('Phone')),
                        'email': safe_str(row.get('Email')),
                        'address': safe_str(row.get('Address')),
                        'opening_balance': safe_decimal(row.get('Opening Balance')),
                    }
                )
                counts['customers'] += 1
        # Suppliers
        if 'Suppliers' in dfs:
            df = dfs['Suppliers']
            for _, row in df.iterrows():
                name = safe_str(row.get('Name'))
                if not name:
                    continue
                Supplier.objects.get_or_create(
                    name=name,
                    defaults={
                        'phone': safe_str(row.get('Phone')),
                        'email': safe_str(row.get('Email')),
                        'address': safe_str(row.get('Address')),
                        'opening_balance': safe_decimal(row.get('Opening Balance')),
                    }
                )
                counts['suppliers'] += 1
        # Products
        if 'Products' in dfs:
            df = dfs['Products']
            for _, row in df.iterrows():
                name = safe_str(row.get('Name'))
                if not name:
                    continue
                cat_name = safe_str(row.get('Category'))
                category = None
                if cat_name:
                    cat, created = Category.objects.get_or_create(name=cat_name)
                    if created:
                        counts['categories'] += 1
                    category = cat
                Product.objects.get_or_create(
                    name=name,
                    defaults={
                        'category': category,
                        'purchase_price': safe_decimal(row.get('Purchase Price')),
                        'selling_price': safe_decimal(row.get('Selling Price')),
                        'gst_percentage': safe_decimal(row.get('GST%')),
                        'stock_quantity': safe_int(row.get('Stock')),
                        'low_stock_alert_qty': safe_int(row.get('Low Stock Alert')),
                        'hsn_code': safe_str(row.get('HSN Code')),
                    }
                )
                counts['products'] += 1
        msg = 'Import complete! '
        if counts['customers']:
            msg += f'{counts["customers"]} customers, '
        if counts['suppliers']:
            msg += f'{counts["suppliers"]} suppliers, '
        if counts['categories']:
            msg += f'{counts["categories"]} categories, '
        if counts['products']:
            msg += f'{counts["products"]} products '
        msg = msg.rstrip(', ') + ' imported.'
        messages.success(request, msg)
        return redirect('dataimport:import')
    return render(request, 'dataimport/import.html')
