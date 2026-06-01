from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Supplier
from .forms import SupplierForm

@login_required
def supplier_list(request):
    search = request.GET.get('search', '')
    suppliers = Supplier.objects.all()
    if search:
        suppliers = suppliers.filter(name__icontains=search)
    context = {'suppliers': suppliers, 'search': search}
    return render(request, 'suppliers/supplier_list.html', context)

@login_required
def supplier_add(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier added successfully.')
            return redirect('suppliers:list')
    else:
        form = SupplierForm()
    return render(request, 'suppliers/supplier_form.html', {'form': form, 'title': 'Add Supplier'})

@login_required
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated successfully.')
            return redirect('suppliers:list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'suppliers/supplier_form.html', {'form': form, 'title': 'Edit Supplier'})

@login_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'Supplier deleted successfully.')
        return redirect('suppliers:list')
    return render(request, 'suppliers/supplier_confirm_delete.html', {'supplier': supplier})
