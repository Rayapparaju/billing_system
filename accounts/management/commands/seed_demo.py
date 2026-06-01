from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from customers.models import Customer
from suppliers.models import Supplier
from products.models import Product, Category
from sales.models import SaleInvoice, SaleItem
from purchases.models import PurchaseInvoice, PurchaseItem
import random
from decimal import Decimal

class Command(BaseCommand):
    help = 'Seed the database with demo data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding demo data...')

        # Categories
        cat_names = ['Electronics', 'Groceries', 'Clothing', 'Stationery', 'Furniture', 'Hardware', 'Pharmaceuticals']
        categories = []
        for name in cat_names:
            cat, _ = Category.objects.get_or_create(name=name)
            categories.append(cat)
        self.stdout.write(f'Created {len(categories)} categories')

        # Customers
        customer_data = [
            ('Rajesh Sharma', '9876543210', 'rajesh@email.com', '12, MG Road, Mumbai', Decimal('5000.00')),
            ('Priya Patel', '9876543211', 'priya@email.com', '45, Ashram Road, Ahmedabad', Decimal('2000.00')),
            ('Amit Singh', '9876543212', 'amit@email.com', '78, Civil Lines, Delhi', Decimal('0.00')),
            ('Sneha Reddy', '9876543213', 'sneha@email.com', '23, Banjara Hills, Hyderabad', Decimal('3500.00')),
            ('Vikram Joshi', '9876543214', 'vikram@email.com', '56, FC Road, Pune', Decimal('1000.00')),
            ('Ananya Gupta', '9876543215', 'ananya@email.com', '90, Salt Lake, Kolkata', Decimal('0.00')),
            ('Rahul Verma', '9876543216', 'rahul@email.com', '34, Gomti Nagar, Lucknow', Decimal('1500.00')),
            ('Deepika Nair', '9876543217', 'deepika@email.com', '67, Panjim, Goa', Decimal('0.00')),
        ]
        for name, phone, email, addr, bal in customer_data:
            Customer.objects.get_or_create(name=name, defaults={
                'phone': phone, 'email': email, 'address': addr, 'opening_balance': bal
            })
        self.stdout.write(f'Created {len(customer_data)} customers')

        # Suppliers
        supplier_data = [
            ('TechDistributors Pvt Ltd', '9988776655', 'info@techdist.com', '100, BKC, Mumbai', Decimal('0.00')),
            ('FreshFoods Trading Co', '9988776656', 'orders@freshfoods.in', '200, Vashi, Navi Mumbai', Decimal('5000.00')),
            ('FashionHub Wholesale', '9988776657', 'sales@fashionhub.in', '50, Tilak Road, Pune', Decimal('0.00')),
            ('OfficeMart Supplies', '9988776658', 'contact@officemart.in', '15, Sarjapur Road, Bangalore', Decimal('3000.00')),
            ('MediLife Distributors', '9988776659', 'info@medilife.in', '88, Civil Hospital Road, Delhi', Decimal('0.00')),
        ]
        for name, phone, email, addr, bal in supplier_data:
            Supplier.objects.get_or_create(name=name, defaults={
                'phone': phone, 'email': email, 'address': addr, 'opening_balance': bal
            })
        self.stdout.write(f'Created {len(supplier_data)} suppliers')

        # Products
        product_data = [
            ('Wireless Mouse', '84716000', 0, 250, 450, 18, 100, 10),
            ('LED Monitor 24"', '85285200', 0, 6500, 9500, 18, 30, 5),
            ('Laptop Bag', '42022200', 2, 400, 800, 12, 50, 10),
            ('Notebook (Pack 5)', '48202000', 3, 60, 120, 5, 200, 20),
            ('Desk Chair', '94013000', 4, 2500, 4500, 18, 15, 5),
            ('Basmati Rice 5kg', '10063090', 1, 250, 380, 5, 80, 10),
            ('Hand Sanitizer 500ml', '38089400', 6, 80, 150, 12, 120, 15),
            ('Cotton T-Shirt', '61091000', 2, 200, 450, 12, 60, 10),
            ('USB-C Hub 7-in-1', '84718000', 0, 800, 1500, 18, 40, 5),
            ('LED Desk Lamp', '94051900', 4, 500, 1200, 18, 25, 5),
            ('Printer Paper A4 (500)', '48025690', 3, 180, 350, 5, 100, 20),
            ('Stainless Steel Bottle', '73239390', 5, 300, 599, 12, 45, 10),
        ]
        for name, hsn, cat_idx, pur, sell, gst, stock, low in product_data:
            Product.objects.get_or_create(name=name, defaults={
                'hsn_code': hsn,
                'category': categories[cat_idx],
                'purchase_price': Decimal(str(pur)),
                'selling_price': Decimal(str(sell)),
                'gst_percentage': Decimal(str(gst)),
                'stock_quantity': stock,
                'low_stock_alert_qty': low,
            })
        self.stdout.write(f'Created {len(product_data)} products')

        customers = list(Customer.objects.all())
        suppliers = list(Supplier.objects.all())
        products = list(Product.objects.all())

        today = date.today()

        # Sales Invoices
        for i in range(20):
            inv_date = today - timedelta(days=random.randint(0, 60))
            customer = random.choice(customers)
            invoice_no = f'SINV-{str(i+1).zfill(5)}'
            num_items = random.randint(1, 4)
            selected = random.sample(products, min(num_items, len(products)))
            subtotal = Decimal('0.00')
            total_gst = Decimal('0.00')
            total_disc = Decimal('0.00')
            items_data = []
            for prod in selected:
                qty = random.randint(1, 10)
                rate = prod.selling_price
                gst_amt = rate * qty * prod.gst_percentage / Decimal('100')
                disc = Decimal(str(random.choice([0, 0, 5, 10, 0])))
                disc_amt = rate * qty * disc / Decimal('100')
                line_total = rate * qty + gst_amt - disc_amt
                subtotal += rate * qty
                total_gst += gst_amt
                total_disc += disc_amt
                items_data.append((prod, qty, rate, prod.gst_percentage, disc_amt, line_total))
            grand_total = subtotal + total_gst - total_disc
            status = random.choice(['Paid', 'Paid', 'Paid', 'Unpaid', 'Partial'])
            invoice = SaleInvoice.objects.create(
                invoice_no=invoice_no,
                customer=customer,
                date=inv_date,
                subtotal=subtotal,
                discount=total_disc,
                gst_amount=total_gst,
                grand_total=grand_total,
                payment_status=status,
            )
            for prod, qty, rate, gst, disc, total in items_data:
                SaleItem.objects.create(
                    invoice=invoice, product=prod, quantity=qty,
                    rate=rate, gst=gst, discount=disc, total=total
                )
                prod.stock_quantity -= qty
                prod.save()
        self.stdout.write('Created 20 sales invoices')

        # Purchase Invoices
        for i in range(10):
            inv_date = today - timedelta(days=random.randint(0, 60))
            supplier = random.choice(suppliers)
            invoice_no = f'PINV-{str(i+1).zfill(5)}'
            num_items = random.randint(1, 4)
            selected = random.sample(products, min(num_items, len(products)))
            subtotal = Decimal('0.00')
            total_gst = Decimal('0.00')
            total_disc = Decimal('0.00')
            items_data = []
            for prod in selected:
                qty = random.randint(5, 25)
                rate = prod.purchase_price
                gst_amt = rate * qty * prod.gst_percentage / Decimal('100')
                disc_amt = Decimal('0')
                line_total = rate * qty + gst_amt
                subtotal += rate * qty
                total_gst += gst_amt
                items_data.append((prod, qty, rate, prod.gst_percentage, disc_amt, line_total))
            grand_total = subtotal + total_gst - total_disc
            status = random.choice(['Paid', 'Paid', 'Unpaid', 'Partial'])
            invoice = PurchaseInvoice.objects.create(
                invoice_no=invoice_no,
                supplier=supplier,
                date=inv_date,
                subtotal=subtotal,
                discount=total_disc,
                gst_amount=total_gst,
                grand_total=grand_total,
                payment_status=status,
            )
            for prod, qty, rate, gst, disc, total in items_data:
                PurchaseItem.objects.create(
                    invoice=invoice, product=prod, quantity=qty,
                    rate=rate, gst=gst, discount=disc, total=total
                )
                prod.stock_quantity += qty
                prod.save()
        self.stdout.write('Created 10 purchase invoices')

        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully!'))
