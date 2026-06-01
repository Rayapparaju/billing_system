from django import forms
from .models import Product, Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name'}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'hsn_code', 'category', 'purchase_price', 'selling_price', 'gst_percentage', 'stock_quantity', 'low_stock_alert_qty']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product name'}),
            'hsn_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter HSN code'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'gst_percentage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'low_stock_alert_qty': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '5'}),
        }
