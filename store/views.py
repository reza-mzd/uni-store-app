from django.shortcuts import render
from django.http import HttpResponse

from . import models
# Create your views here.

def hello_world(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR')
    
    if ip:
        ip = ip.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    return HttpResponse(f"Your IP Address is: {ip}")

def show_products(request):
    html = ''
    products = models.Product.objects.all()
    for product in products:
        html += product.name + "<br/>"
    
    return HttpResponse(html) 

        
    
