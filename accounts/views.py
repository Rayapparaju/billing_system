from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.management import call_command
from io import StringIO
from .models import Company

def home(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Welcome back!')
            return redirect('dashboard:home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirm', '')
        company_name = request.POST.get('company_name', '').strip() or 'My Company'
        company_address = request.POST.get('company_address', '').strip()
        company_phone = request.POST.get('company_phone', '').strip()
        company_gst = request.POST.get('company_gst', '').strip()
        if not username or not password:
            messages.error(request, 'Username and password are required.')
        elif password != confirm:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            Company.objects.create(
                user=user, name=company_name,
                address=company_address, phone=company_phone,
                gst_number=company_gst, email=email,
            )
            login(request, user)
            messages.success(request, f'Welcome {username}! Account created.')
            return redirect('dashboard:home')
    return render(request, 'accounts/register.html')

@login_required
def company_view(request):
    company, _ = Company.objects.get_or_create(user=request.user, defaults={'name': 'My Company'})
    if request.method == 'POST':
        company.name = request.POST.get('name', company.name)
        company.address = request.POST.get('address', '')
        company.phone = request.POST.get('phone', '')
        company.email = request.POST.get('email', '')
        company.gst_number = request.POST.get('gst_number', '')
        company.website = request.POST.get('website', '')
        company.save()
        messages.success(request, 'Company details updated.')
        return redirect('accounts:company')
    return render(request, 'accounts/company.html', {'company': company})

def setup_view(request):
    if User.objects.filter(is_superuser=True).exists():
        messages.info(request, 'Already set up. Login below.')
    else:
        buf = StringIO()
        call_command('seed_demo', stdout=buf)
        messages.success(request, 'Demo data loaded! Login with admin / admin123')
    return redirect('accounts:login')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('accounts:home')
