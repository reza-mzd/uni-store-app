from django.shortcuts import render
from django.http import HttpResponse
from . import forms
from . import models
from django.views import View
# Create your views here.

def hello_world(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR')
    
    if ip:
        ip = ip.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    return HttpResponse(f"Your IP Address is: {ip}")

# def show_products(request):
#     html = ''
#     products = models.Product.objects.all()
#     for product in products:
#         html += product.name + "<br/>"
    
#     return HttpResponse(html) 

class ProductListview(View):
    
    def get(self, request):
        products = models.Product.objects.all()

        # context = {'objs': products}
        return render(request, 'store/product_list.html', {'objs': products})
        
    
class TestFormView(View):
    
    def get(self, request):
        form = forms.MyForm()
        return render(request, 'store/testform.html', {'form': form})
    
    def post(self, request):
        
        form = forms.MyForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
        
            return render(request, 'store/showresult.html', {'u': username, 'p': password})
        
        return render(request, 'store/testform.html', {'form': form})