from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Customer
from .forms import CustomerForm

@login_required
def customer_list(request):
    search = request.GET.get('search', '')
    customers = Customer.objects.all()
    if search:
        customers = customers.filter(name__icontains=search)
    context = {'customers': customers, 'search': search}
    return render(request, 'customers/customer_list.html', context)

@login_required
def customer_add(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer added successfully.')
            return redirect('customers:list')
    else:
        form = CustomerForm()
    return render(request, 'customers/customer_form.html', {'form': form, 'title': 'Add Customer'})

@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully.')
            return redirect('customers:list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'customers/customer_form.html', {'form': form, 'title': 'Edit Customer'})

@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully.')
        return redirect('customers:list')
    return render(request, 'customers/customer_confirm_delete.html', {'customer': customer})
