from django import forms
from .models import *

class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['name', 'dob', 'gender', 'phone', 'email']

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = '__all__'

        widgets = {
            'code': forms.TextInput(),
            'discount': forms.TextInput(),
            'quantity': forms.TextInput(),
            'condition': forms.TextInput(),
            'start_date': forms.DateInput(),
            'end_date': forms.DateInput(),
        }


class ProductForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all())

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category']

        widgets = {
            'name': forms.TextInput(),
            'description': forms.TextInput(),
            'price': forms.TextInput(),
        }


class ProductSaleForm(forms.ModelForm):
    class Meta:
        model = ProductSale
        fields = ['price']

        widgets = {
            'price': forms.TextInput(),
        }


class ProductImageForm(forms.ModelForm):
    name = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))  # thêm thuộc tính multiple

    class Meta:
        model = ProductImage
        fields = ['name']

class AddressShippingForm(forms.ModelForm):
    class Meta:
        model = AddressShipping
        fields = ['receiver', 'phone', 'address']

        widgets = {
            'receiver': forms.TextInput(),
            'phone': forms.TextInput(),
            'address': forms.TextInput(),
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ['date', 'customer', 'status']

# class OrderStatusForm(forms.ModelForm):
#     class Meta:
#         model = OrderStatus
#         fields = ['name', 'description']