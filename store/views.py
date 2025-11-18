from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from . import forms
from . import models
from django.views import View


# def hello_world(request):
#     ip = request.META.get('HTTP_X_FORWARDED_FOR')
    
#     if ip:
#         ip = ip.split(',')[0]
#     else:
#         ip = request.META.get('REMOTE_ADDR')
    
#     return HttpResponse(f"Your IP Address is: {ip}")

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

from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
class ProductDetailView(View):
    def get(self, request, pid):
        try:
            obj = models.Product.objects.get(id=pid)
            comments = obj.comments.filter(is_approved=True).prefetch_related('user').order_by('-date')
            form = forms.CommentForm()
            return render(request, 'store/product_details.html',
                          {'obj': obj, 'form': form, 'comments': comments})
        except models.Product.DoesNotExist:
            return render(request, 'store/product_404.html') 
        
        # obj = get_object_or_404(models.Product, id=pid)   # we can use this line instead of try-except method

from django.shortcuts import reverse
class CommentsView(View):
    def post(self, request, pid):
        product = get_object_or_404(models.Product, id=pid)
        form = forms.CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.product = product
            comment.user = request.user
            comment.save()         
            return HttpResponseRedirect(reverse('store:product-detail', kwargs={"pid":pid}))
        return render(request, 'store/product_details.html', {'obj': product, 'form': form})