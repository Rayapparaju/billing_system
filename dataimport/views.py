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

def col_map(cols):
    cm = {}
    for c in cols:
        cl = str(c).strip().lower().replace(' ', '').replace('_', '').replace('-', '')
        cm[cl] = c
    return cm

def get_val(row, cm, *variants):
    for v in variants:
        vl = v.lower().replace(' ', '').replace('_', '').replace('-', '')
        if vl in cm:
            return row[cm[vl]]
    return None

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

        sheet_names = list(dfs.keys())
        detected = f'Detected sheets: {", ".join(sheet_names)}'

        counts = {'customers': 0, 'suppliers': 0, 'products': 0, 'categories': 0}
        any_found = False

        for sheet_name, df in dfs.items():
            sl = sheet_name.strip().lower().replace(' ', '').replace('_', '').replace('-', '')
            cm = col_map(df.columns)

            if 'customer' in sl:
                any_found = True
                for _, row in df.iterrows():
                    name = safe_str(get_val(row, cm, 'Name', 'Customer Name', 'CustomerName'))
                    if not name:
                        continue
                    Customer.objects.get_or_create(
                        name=name,
                        defaults={
                            'phone': safe_str(get_val(row, cm, 'Phone', 'Mobile', 'Contact', 'Phone No', 'PhoneNo')),
                            'email': safe_str(get_val(row, cm, 'Email', 'E-mail', 'Mail')),
                            'address': safe_str(get_val(row, cm, 'Address', 'Addr')),
                            'opening_balance': safe_decimal(get_val(row, cm, 'Opening Balance', 'OpeningBalance', 'Balance', 'Opening')),
                        }
                    )
                    counts['customers'] += 1

            elif 'supplier' in sl:
                any_found = True
                for _, row in df.iterrows():
                    name = safe_str(get_val(row, cm, 'Name', 'Supplier Name', 'SupplierName'))
                    if not name:
                        continue
                    Supplier.objects.get_or_create(
                        name=name,
                        defaults={
                            'phone': safe_str(get_val(row, cm, 'Phone', 'Mobile', 'Contact', 'Phone No', 'PhoneNo')),
                            'email': safe_str(get_val(row, cm, 'Email', 'E-mail', 'Mail')),
                            'address': safe_str(get_val(row, cm, 'Address', 'Addr')),
                            'opening_balance': safe_decimal(get_val(row, cm, 'Opening Balance', 'OpeningBalance', 'Balance', 'Opening')),
                        }
                    )
                    counts['suppliers'] += 1

            elif 'product' in sl or 'item' in sl:
                any_found = True
                for _, row in df.iterrows():
                    name = safe_str(get_val(row, cm, 'Name', 'Product Name', 'ProductName', 'Item Name', 'ItemName'))
                    if not name:
                        continue
                    cat_name = safe_str(get_val(row, cm, 'Category', 'Cat', 'Product Category', 'ProductCategory'))
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
                            'purchase_price': safe_decimal(get_val(row, cm, 'Purchase Price', 'PurchasePrice', 'Cost Price', 'CostPrice', 'Buying Price', 'BuyingPrice')),
                            'selling_price': safe_decimal(get_val(row, cm, 'Selling Price', 'SellingPrice', 'Sale Price', 'SalePrice', 'Price', 'Rate', 'MRP')),
                            'gst_percentage': safe_decimal(get_val(row, cm, 'GST%', 'GST', 'GST Percentage', 'GstPercentage', 'Tax%', 'Tax')),
                            'stock_quantity': safe_int(get_val(row, cm, 'Stock', 'Quantity', 'Qty', 'Stock Quantity', 'StockQuantity', 'Opening Stock', 'OpeningStock')),
                            'low_stock_alert_qty': safe_int(get_val(row, cm, 'Low Stock Alert', 'LowStockAlert', 'Alert Quantity', 'AlertQty', 'Min Stock', 'MinStock')),
                            'hsn_code': safe_str(get_val(row, cm, 'HSN Code', 'HSNCode', 'HSN', 'HSN No', 'HSNNo', 'Code')),
                        }
                    )
                    counts['products'] += 1

        if not any_found:
            messages.error(request, f'No matching sheets found. {detected}. Expected sheet names containing: Customers, Suppliers, or Products/Items.')
            return redirect('dataimport:import')

        msg = f'Import complete! {detected}. '
        parts = []
        if counts['customers']:
            parts.append(f'{counts["customers"]} customers')
        if counts['suppliers']:
            parts.append(f'{counts["suppliers"]} suppliers')
        if counts['categories']:
            parts.append(f'{counts["categories"]} categories')
        if counts['products']:
            parts.append(f'{counts["products"]} products')
        if parts:
            msg += ', '.join(parts) + ' imported.'
        else:
            msg += 'No new records created (0 rows found).'
        messages.success(request, msg)
        return redirect('dataimport:import')
    return render(request, 'dataimport/import.html')
