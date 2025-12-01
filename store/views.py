from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseRedirect
from . import forms
from . import models
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from zeep import Client
from django.contrib.sites.shortcuts import get_current_site
from zeep.exceptions import TransportError 
from requests.exceptions import HTTPError


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


from django.http import JsonResponse
class CartAddView(View):
    def get(self, request, pid):
        obj = get_object_or_404(models.Product, id=pid)
        cart = request.session.get('cart', {})
        id = str(obj.id)
        if id in cart:
            cart[id] += 1
        else:
            cart[id] = 1
        
        request.session['cart'] = cart
        ids = list(cart.keys())
        objects = models.Product.objects.filter(id__in=ids)

        total_price = 0
        total_count = 0
        for id, count in cart.items():
            total_count += count
            cobj = objects.get(id=id)
            total_price += (cobj.price - cobj.price*cobj.discount/100) * count
        return JsonResponse({'cart': cart, 'total_count': total_count,
                            'total_price': total_price})


# class CartRemoveView(View):
#     def get(self, request, pid):
#         obj = get_object_or_404(models.Product, id=pid)
#         cart = request.session.get('cart', {})
#         id = str(obj.id)
#         if id in cart:
#             del cart[id]
            
#         request.session['cart'] = cart
#         return HttpResponseRedirect(reverse('store:product_list'))    
def get_cart_details(request):
        
    cart = request.session['cart']
    ids = list(cart.keys())
    objects = models.Product.objects.filter(id__in=ids)
    cart_info = {}
    total_price = 0
    for id, count in cart.items():
        p = objects.get(id=id)
        price = (p.price - p.price*p.discount/100) * count
        cart_info[id] = {'obj': p, 'count': count, 'price': int(price)}
        total_price += price
    return cart, cart_info, total_price


class CartDetailsView(View):
    
    def get(self, request):
        _, cart_info, total_price = get_cart_details(request)
        return render(request, 'store/cart.html', {'cart': cart_info,
                                                   'price': total_price})


from django.db import transaction, IntegrityError
class CheckoutView(LoginRequiredMixin, View):
    def get(self, request):
        _, cart_info, total_price = get_cart_details(request)
        form = forms.InvoiceForm()
        return render(request, 'store/invoice_page1.html', {'cart': cart_info,
                                                            'price': total_price,
                                                            'form': form})
        
    
    def post(self, request):
        _, cart_info, total_price = get_cart_details(request)
        form = forms.InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.user = request.user
            invoice.total = total_price
            items = []
            for pid,item in cart_info.items():
                o = models.InvoiceItem(product=item['obj'],
                                       invoice=invoice,
                                       price=item['obj'].price,
                                       discount=item['obj'].discount,
                                       name=item['obj'].name,
                                       total=item['price'],
                                       count=item['count'])
                items.append(o)
            try:
                with transaction.atomic():
                    invoice.save()
                    items = models.InvoiceItem.objects.bulk_create(items)
                    payment = models.Payment(invoice=invoice,
                                             amount=invoice.total,
                                             description=f'My Invoice',
                                             phone=invoice.phone)
                    client = Client('https://sandbox.zarinpal.com/pg/services/WebGate/wsdl')
                    site = get_current_site(request)
                    domain = site.domain
                    res = client.service.PaymentRequest('XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX',
                                                        payment.amount,
                                                        payment.description,
                                                        request.user.email,
                                                        payment.phone,
                                                        f"http://{domain}{reverse('store:payment_verify')}")
                    if res.Status == 100:   
                        payment.authority = res.Authority
                        payment.save()
                        return redirect(f'https://sandbox.zarinpal.com/pg/StartPay/{payment.authority}')
                    else:
                        raise RuntimeError(f'Zarinpal Status {res.Status}')
            except RuntimeError: 
                transaction.rollback()
                return render(request, 'store/invoice_process_error.html', 
                              {'message': 'Payment failed: Logical error from the payment gateway.'})
            
            except (TransportError, HTTPError) as e: 
                transaction.rollback()
                return render(request, 'store/invoice_process_error.html', 
                              {'message': 'Communication error with the payment gateway (Check network/proxy).'})

            except Exception as e:
                transaction.rollback()
                return render(request, 'store/invoice_process_error.html', 
                              {'message': 'Internal error in the checkout process.'})
            
        return render(request, 'store/invoice_page1.html', {'cart': cart_info,
                                                            'price': total_price,
                                                            'form': form})



class PaymentVerifyView(LoginRequiredMixin, View):
    
    def get(self, request):
        status = request.GET.get('Status')
        authority = request.GET.get('Authority')
        payment = get_object_or_404(models.Payment, authority=authority,
                                                    state = models.Payment.STATE.PENDING)
        if status == "OK":
            client = Client('https://sandbox.zarinpal.com/pg/services/WebGate/wsdl?WSDL')
            res = client.service.PaymentVerification('XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX',
                                                payment.authority,
                                                payment.amount)
            if res.Status == 100:
                payment.refid = res.RefID
                payment.state = models.Payment.STATE.COMPLETE
                payment.invoice.state = models.Invoice.STATE.STATE_COMPLETED
                payment.save()
                payment.invoice.save()
                return render(request, "store/payment_ok.html",{'refid': payment.refid})
            else:
                payment.state = models.Payment.STATE.ERROR
                payment.invoice.state = models.Invoice.STATE.STATE_CANCELED
                payment.save()
                payment.invoice.save()
                return render(request, 'store/payment_failed.html')
                
        else:
            payment.state = models.Payment.STATE.ERROR
            payment.save()
            return render(request, 'store/payment_failed.html')