from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('yourIP/', views.hello_world),
    path('product/', views.show_products, name='product_list'),
]
