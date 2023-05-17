from django import forms
from .models import *


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
    name = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True}))  # thêm thuộc tính multiple

    class Meta:
        model = ProductImage
        fields = ['name']


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = OrderStatus
        fields = ['name', 'description']