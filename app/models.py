from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# Create your models here.
class User(AbstractUser):
    name = models.CharField(max_length=100, blank=False, null=False)
    # avatar = models.ImageField(upload_to='user/')
    dob = models.DateField(blank=False, null=True)
    gender = models.CharField(max_length=50, blank=False, null=False)
    phone = models.CharField(max_length=20, blank=False, null=False)
    email = models.EmailField(max_length=50, blank=False, null=False)
    is_staff = models.IntegerField(default=0, blank=False, null=False)


class Category(models.Model):
    category_id = models.AutoField(primary_key=True, blank=False, null=False)
    name = models.CharField(max_length=100, blank=False, null=False)

    def __str__(self):
        return self.name


class Product(models.Model):
    product_id = models.AutoField(primary_key=True, blank=False, null=False)
    name = models.CharField(max_length=100, blank=False, null=False)
    description = models.CharField(max_length=1000, blank=False, null=False)
    price = models.FloatField(blank=False, null=False)
    time_created = models.DateTimeField(default=timezone.datetime.now(), blank=False, null=False)
    rating = models.FloatField(default=0, blank=False, null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=False, null=False)
    total_sold = models.IntegerField(default=0, blank=False, null=False)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    image_id = models.AutoField(primary_key=True, blank=False, null=False)
    name = models.ImageField(upload_to='product/')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=False, null=False)

    def __str__(self):
        return self.product.name


class ProductDetail(models.Model):
    detail_id = models.AutoField(primary_key=True, blank=False, null=False)
    color = models.CharField(max_length=20, blank=False, null=False)
    size = models.CharField(max_length=20, blank=False, null=False)
    quantity = models.IntegerField(default=0, blank=False, null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=False, null=False)

    def __str__(self):
        return f"{self.color} - {self.size} - {self.quantity}"


class ProductSale(models.Model):
    sale_id = models.AutoField(primary_key=True, blank=False, null=False)
    price = models.FloatField(default=0, blank=False, null=False)
    start_date = models.DateTimeField(default=timezone.datetime.now(), blank=False, null=False)
    end_date = models.DateTimeField(default=timezone.datetime.now(), blank=False, null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=False, null=False)

    def __str__(self):
        return self.product.name


class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True, blank=False, null=False)
    comment = models.CharField(max_length=255, blank=True, null=False)
    rating = models.IntegerField(blank=False, null=False)
    date = models.DateTimeField(default=timezone.datetime.now(), blank=False, null=False)
    like = models.IntegerField(default=1, blank=False, null=False)
    dislike = models.IntegerField(default=0, blank=False, null=False)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=False, null=False)

    def __str__(self):
        return f"{self.product} - {self.customer}"


class FeedbackImage(models.Model):
    feedback_image_id = models.AutoField(primary_key=True, blank=False, null=False)
    name = models.CharField(max_length=100, blank=False, null=False)
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.name


class FeedbackRespone(models.Model):
    feedback_respone_id = models.AutoField(primary_key=True, blank=False, null=False)
    comment = models.CharField(max_length=255, blank=False, null=False)
    date = models.DateTimeField(default=timezone.datetime.now(), blank=False, null=False)
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return f"{self.feedback} - {self.feedback_respone_id}"


class AddressShipping(models.Model):
    address_shipping_id = models.AutoField(primary_key=True, blank=False, null=False)
    receiver = models.CharField(max_length=100, blank=False, null=False)
    phone = models.CharField(max_length=20, blank=False, null=False)
    address = models.CharField(max_length=255, blank=False, null=False)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)

    def __str__(self):
        return self.receiver


class Order(models.Model):
    order_id = models.AutoField(primary_key=True, blank=False, null=False)
    date = models.DateTimeField(default=timezone.datetime.now(), blank=False, null=False)
    discount = models.FloatField(default=0, blank=False, null=False)
    shipping = models.FloatField(default=0, blank=False, null=False)
    total = models.FloatField(blank=False, null=False)
    note = models.CharField(max_length=100, blank=True, null=False)
    payment_method = models.CharField(max_length=100, blank=False, null=False)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    address_shipping = models.ForeignKey(AddressShipping, on_delete=models.CASCADE, blank=False, null=False)


class OrderItem(models.Model):
    oder_item_id = models.AutoField(primary_key=True, blank=False, null=False)
    size = models.CharField(max_length=20, blank=False, null=False)
    color = models.CharField(max_length=20, blank=False, null=False)
    quantity = models.IntegerField(default=1, blank=False, null=False)
    price = models.FloatField(blank=False, null=False)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=False, null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=False, null=False)


class OrderStatus(models.Model):
    order_status_id = models.AutoField(primary_key=True, blank=False, null=False)
    name = models.CharField(max_length=100, blank=False, null=False)
    description = models.CharField(max_length=255, blank=False, null=False)


class Tracking(models.Model):
    track_id = models.AutoField(primary_key=True, blank=False, null=False)
    date = models.DateTimeField(default=timezone.datetime.now(), blank=False, null=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=False, null=False)
    order_status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE, blank=False, null=False)


class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True, blank=False, null=False)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)


class CartItem(models.Model):
    cart_item_id = models.AutoField(primary_key=True, blank=False, null=False)
    color = models.CharField(max_length=20, blank=False, null=False)
    size = models.CharField(max_length=20, blank=False, null=False)
    quantity = models.IntegerField(default=1, blank=False, null=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, blank=False, null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=False, null=False)


class Coupon(models.Model):
    coupon_id = models.AutoField(primary_key=True, blank=False, null=False)
    code = models.CharField(max_length=100, blank=False, null=False)
    discount = models.FloatField(default=0, blank=False, null=False)
    quantity = models.IntegerField(default=0, blank=False, null=False)
    condition = models.FloatField(default=1, blank=False, null=False)
    start_date = models.DateTimeField(default=timezone.datetime.now(), blank=False, null=False)
    end_date = models.DateTimeField(default=timezone.datetime.now(), blank=False, null=False)


class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True, blank=False, null=False)
    content = models.CharField(max_length=255, blank=False, null=False)
    create_at = models.DateTimeField(default=timezone.datetime.now(), blank=False, null=False)
