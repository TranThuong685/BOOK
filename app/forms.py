from django import forms
from .models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit


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
        fields = ['name', 'description', 'price', 'category', 'sale', 'page', 'age', 'author', 'publisher', 'translator', 'year_of_publish',
                  'size', 'weight']

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
    name = forms.FileField(widget=forms.ClearableFileInput(
        attrs={'multiple': True}))  # thêm thuộc tính multiple

    class Meta:
        model = ProductImage
        fields = ['name']

    def __init__(self, *args, **kwargs):
        # Tùy chọn này giúp trường 'name' không bắt buộc
        super().__init__(*args, **kwargs)
        self.fields['name'].required = False 


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


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = OrderStatus
        fields = ['name', 'description']


class ResponseForm(forms.Form):
    textfield = forms.CharField(label="Nhập vào phản hồi cho bình luận", 
                                 widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '5', 'cols': '80'}))
    

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.add_input(Submit('submit', 'Gửi phản hồi'))

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        category_id = self.instance.category_id  # Lấy ID của bản ghi hiện tại (nếu đang chỉnh sửa)
        
        # Kiểm tra nếu name đã tồn tại với các record khác, bỏ qua record hiện tại khi edit
        if Category.objects.filter(name=name).exclude(category_id=category_id).exists():
            raise forms.ValidationError("Tên danh mục đã tồn tại, vui lòng chọn tên khác.")
        
        return name