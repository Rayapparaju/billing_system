from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category
from .forms import ProductForm, CategoryForm

@login_required
def product_list(request):
    search = request.GET.get('search', '')
    products = Product.objects.select_related('category').all()
    if search:
        products = products.filter(name__icontains=search)
    context = {'products': products, 'search': search}
    return render(request, 'products/product_list.html', context)

@login_required
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully.')
            return redirect('products:list')
    else:
        form = ProductForm()
    return render(request, 'products/product_form.html', {'form': form, 'title': 'Add Product'})

@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('products:list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/product_form.html', {'form': form, 'title': 'Edit Product'})

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('products:list')
    return render(request, 'products/product_confirm_delete.html', {'product': product})

@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'products/category_list.html', {'categories': categories})

@login_required
def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully.')
            return redirect('products:category_list')
    else:
        form = CategoryForm()
    return render(request, 'products/category_form.html', {'form': form, 'title': 'Add Category'})

@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('products:category_list')
    return render(request, 'products/category_confirm_delete.html', {'category': category})
