from django.urls import path
from . import views

urlpatterns = [
    path('login', views.log_in, name='login'),
    path('logout', views.log_out, name='logout'),
    path('home', views.home, name='home'),
    path('list-product', views.listProduct, name='list-product'),
    path('product/<int:product_id>', views.getProductDetail, name='product-detail'),
    path('cart', views.add_to_cart, name='cart'),
    path('edit-cart-item', views.edit_cart_item, name='edit-cart-item'),
    path('delete-cart-item', views.delete_cart_item, name='delete-cart-item'),
    path('check-coupon', views.check_coupon, name='check-coupon'),
    path('checkout', views.checkout, name='check-out'),
    # API
    path('filter-product', views.getListProduct, name='list-product'),
]
