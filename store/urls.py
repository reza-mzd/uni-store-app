from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # path('yourIP/', views.hello_world),
    path('', views.ProductListview.as_view(), name='product_list'),
    path('test-form', views.TestFormView.as_view(), name='test-form'),
    # /product/?id=12
    # /product-12
    # /product/12
    # /product/slug-of-product-12
    # /product/slug-of/product/12
    # /product/12/slug-of/product
    path('product/<int:pid>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('product/<int:pid>/comments', views.CommentsView.as_view(), name='comments')
]
