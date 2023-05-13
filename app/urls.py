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
    path('register', views.register, name='register'),
    # path('admin/orders', views.orders_admin, name='admin_orders'),

    path('coupons', views.couponManager, name='coupons'),
    path('add_coupon', views.addCoupon, name='add_coupon'),
    path('add_product', views.addProduct, name='add_product'),
    path('products', views.productManager, name='products'),
    path('delete_product/<int:product_id>', views.deleteProduct, name='delete_product'),
]
