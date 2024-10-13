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
    path('buynow', views.buy_now, name='buy-now'),
    path('get-order', views.get_order, name='get_order'),
    path('order-detail', views.get_order_detail, name='order-detail'),
    path('cancel-order', views.cancel_order, name='cancel-order'),
    path('customers', views.customerManager, name='customers'),
    path('admin_orders', views.orderManager, name='admin_orders'),
    # API
    path('filter-product', views.getListProduct, name='list-product'),
    path('add-address', views.add_address, name='add-address'),
    path('register', views.register, name='register'),
    path('order', views.order, name='order'),

    path('feedback', views.handleFeedback, name='feedback'),
    path('list-feedback', views.getFeedback, name='list-feedback'),
    path('get-feedback', views.getFeedbackByProduct, name='get-feedback'),

    path('list-coupon', views.getCoupon, name='list-coupon'),
    path('profile', views.profile, name='profile'),
    path('notification', views.notification, name='notification'),

    #coupon
    path('coupons', views.couponManager, name='coupons'),
    path('add_coupon', views.addCoupon, name='add_coupon'),
    path('edit_coupon', views.editCoupon, name='edit_coupon'),
    path('delete_coupon', views.deleteCoupon, name='delete_coupon'),

    # product
    path('products', views.productManager, name='products'),
    path('add_product', views.addProduct, name='add_product'),
    path('edit_product', views.editProduct, name='edit_product'),
    path('product-detail', views.getProductDetailAdmin, name='product_detail_admin'),
    path('delete_product', views.deleteProduct, name='delete_product'),

    # category
    path('categories', views.categoryManager, name='categories'),
    path('add_category', views.addCategory, name='add_category'),
    path('edit_category', views.editCategory, name='edit_category'),
    path('delete_category', views.deleteCategory, name='delete_category'),

    path('order_detail', views.getOrderDetail, name='order_datail'),
    path('report', views.report, name='report'),
    path('view_profile', views.viewProfile, name='view_profile'),
]
