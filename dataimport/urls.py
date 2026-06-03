from django.urls import path
from . import views

app_name = 'dataimport'

urlpatterns = [
    path('', views.import_excel, name='import'),
]
