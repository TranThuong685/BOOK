from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register([User, Category, Product, ProductImage, ProductDetail, ProductSale, Coupon, Notification, OrderStatus])

