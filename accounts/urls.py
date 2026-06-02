from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('setup/', views.setup_view, name='setup'),
    path('company/', views.company_view, name='company'),
    path('logout/', views.logout_view, name='logout'),
]
