from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.db.models import F, FloatField, ExpressionWrapper, Sum, Value, CharField, Case, When, DateTimeField
from django.db.models.functions import Coalesce, Round
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from .serializers import ProductSerializer, FeedbackSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import locale
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from .forms import *
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms import formset_factory
from datetime import datetime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def log_in(request):
    if request.method == 'GET':
        return render(request, 'customer/login.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('/admin/orders')
            return redirect('/home')
        else:
            return render(request, 'customer/login.html', {'error': 'Tên đăng nhập hoặc mật khẩu không đúng'})


def log_out(request):
    logout(request)
    return redirect('/home')


def register(request):
    if request.method == 'GET':
        return render(request, 'customer/home.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        repassword = request.POST.get('repassword')
        if password != repassword:
            message = 'Mật khẩu không khớp nhau'
        else:
            if User.objects.filter(username=username).exists():
                message = 'Tài khoản đã có người sử dụng'
            else:
                user = User(username=username)
                user.set_password(password)
                user.save()
                message = 'Đăng ký tài khoản thành công'
        print(message)
        return render(request, 'customer/login.html', {'messages': message})


# def order_admin(request):


def home(request):
    now = timezone.now()

    products = Product.objects.annotate(
                    curr_price=Case(
                        When(productsale__start_date__lte=now,
                                productsale__end_date__gte=now,
                                then=F('productsale__price')),
                        default=F('price'),
                        output_field=FloatField()
                    ),
                    discount_percent=ExpressionWrapper(
                        Coalesce((1 - F('curr_price') / F('price')) * 100, 0),
                        output_field=FloatField()
                    ),
                )

    top_selling_products = products.order_by('-total_sold')[:10]

    top_sale_products = products.order_by('-discount_percent')[:10]

    hot_selling_product = (products.filter(orderitem__order__date__month=now.month,
                                    orderitem__order__date__year=now.year)
                                    .annotate(total_sold_month=Sum('orderitem__quantity'))
                                    .order_by('-total_sold_month')
                            )[:10]
    
    context = {
        'top_selling_products': top_selling_products,
        'top_sale_products': top_sale_products,
        'hot_selling_products': hot_selling_product,
        'range': range(10)
    }

    return render(request, 'customer/home.html', context)


def listProduct(request):
    categories = Category.objects.all()
    search = request.GET.get('search')

    context = {
        'categories': categories,
        'search': search
    }
    return render(request, 'customer/list-product.html', context)


@api_view(['GET'])
def getListProduct(request):
    
    search = request.GET.get('search')
    
    category = request.GET.get('category')
    if category:
        category = [int(category) for category in category.split(',')]

    status = request.GET.get('status')
    if status:
        status = [status for status in status.split(',')]

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    rating = request.GET.get('rating')
    sort = request.GET.get('sort')
    top_sale_products = request.GET.get('top_sale_products')
    top_selling_products = request.GET.get('top_selling_products')
    best_selling_product = request.GET.get('best_selling_product')

    products = Product.objects.annotate(
        curr_price=Case(
            When(productsale__start_date__lte=timezone.now(),
                 productsale__end_date__gte=timezone.now(),
                 then=F('productsale__price')),
            default=F('price'),
            output_field=FloatField()
        ),
        discount_percent=ExpressionWrapper(
            Coalesce((1 - F('curr_price') / F('price')) * 100, 0),
            output_field=FloatField()
        ),
        quantity=Sum('productdetail__quantity')
    )
    if search is not None and search != '':
        products = products.filter(name__icontains=search)

    if category:
        categories = Category.objects.filter(category_id__in=category)
        products = products.filter(category__in=categories)
    
    if status and len(status) == 1:
        if status[0] == 'instock':
            products = products.filter(quantity__gt=0)
        elif status[0] == 'outstock':
            products = products.filter(quantity=0)

    if min_price:
        products = products.filter(price__gte=int(min_price))

    if max_price:
        products = products.filter(price__lte=int(max_price))

    if rating:
        products = products.filter(rating__gte=rating)


    
    
    if top_sale_products:
        now = timezone.now()
        products = products.order_by('-discount_percent')

    if top_selling_products:
        products = products.order_by('-total_sold')

    if best_selling_product:
        now = timezone.now()
        products = (products.filter(
                                orderitem__order__date__month=now.month,
                                orderitem__order__date__year=now.year
                            ).annotate(
                                total_sold_month=Sum('orderitem__quantity')
                            ).order_by('-total_sold_month')
                            )
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    else :
        products = products.order_by('-total_sold')

    paginator = PageNumberPagination()
    paginator.page_query_param = 'page'
    paginator.page_size = 20
    result_page = paginator.paginate_queryset(products, request)
    serializer = ProductSerializer(result_page, many=True,context={'request': request})

    respone = paginator.get_paginated_response(serializer.data)
    respone.data['current_page'] = paginator.page.number
    respone.data['total_page'] = paginator.page.paginator.num_pages
    return respone

def getProductDetail(request, product_id):
    product = Product.objects.filter(pk=product_id).annotate(
        curr_price=Case(
            When(productsale__start_date__lte=timezone.now(),
                 productsale__end_date__gte=timezone.now(),
                 then=F('productsale__price')),
            default=F('price'),
            output_field=FloatField()
        ),
        discount_percent=ExpressionWrapper(
            Coalesce((1 - F('curr_price') / F('price')) * 100, 0),
            output_field=FloatField()
        ),
        quantity=Sum('productdetail__quantity')
    ).first()

    sales = product.productsale_set.filter(start_date__lte=timezone.now(), end_date__gte=timezone.now()).first()
    feedbacks = Feedback.objects.filter(product=product).order_by('-date')
    num_feedbacks = feedbacks.count()
    feedback_paginator = Paginator(feedbacks, 5)
    feedback_page = request.GET.get('page')
    feedbacks = feedback_paginator.get_page(feedback_page)
    
    related_products = (Product.objects
                        .filter(category=product.category)
                        .exclude(pk=product.pk)
                        )[:10].annotate(
                            curr_price=Case(
                            When(productsale__start_date__lte=timezone.now(),
                                productsale__end_date__gte=timezone.now(),
                                then=F('productsale__price')),
                            default=F('price'),
                            output_field=FloatField()
                            ),
                            discount_percent=ExpressionWrapper(
                                    Coalesce((1 - F('curr_price') / F('price')) * 100, 0),
                                    output_field=FloatField()
                            )
                        )

    context = {
        'product': product,
        'sales': sales,
        'num_feedbacks': num_feedbacks,
        'feedbacks': feedbacks,
        'related_products': related_products
    }
    return render(request, 'customer/product_detail.html', context)


@login_required(login_url='/login')
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def add_to_cart(request):
    if request.method == 'GET':
        cart = Cart.objects.filter(customer=request.user).last()
        if not cart:
            cart = Cart.objects.create(customer=request.user)
        cartitems = CartItem.objects.filter(cart=cart)
        cartitems = cartitems.annotate(
            price=Case(
                When(product__productsale__start_date__lte=timezone.now(), 
                    product__productsale__end_date__gte=timezone.now(),
                    then=F('product__productsale__price')),
                default=F('product__price'),
                output_field=FloatField()
            ),
            total_price=ExpressionWrapper(F('price') * F('quantity'), output_field=FloatField())
        )
        context = {
            'cart': cart,
            'cartitems': cartitems
        }
        return render(request, 'customer/cart.html', context = context)
    
    if request.method == 'POST':
        id = request.POST.get('product_id')
        product = get_object_or_404(Product, pk=id)

        color = request.POST.get('color')
        size = request.POST.get('size')
        quantity = request.POST.get('quantity')
        quantity = int(quantity)

        if 'cart_id' in request.session:
            cart_id = request.session['cart_id']
            cart = Cart.objects.get(pk=cart_id)
        else:
            cart = Cart.objects.create(customer=request.user)
            request.session['cart_id'] = cart.cart_id
        
        cart_item = CartItem.objects.filter(cart=cart, product=product, color=color, size=size).first()
        product_detail = ProductDetail.objects.filter(product=product, color=color, size=size).first()
        if cart_item:
            if cart_item.quantity + quantity > product_detail.quantity:
                return JsonResponse({'status': 'error', 'message': 'Số lượng sản phẩm không đủ, trong giỏ hàng đã có ' + str(cart_item.quantity) + ' sản phẩm'})
        else:
            cart_item = CartItem.objects.create(cart=cart, product=product, color=color, size=size, quantity=quantity)
        cart_item.save()

        return JsonResponse({'status': 'success', 'message': 'Thêm vào giỏ hàng thành công'})

def edit_cart_item(request):
    cart_item_id = request.POST.get('cart_item_id')
    quantity = request.POST.get('quantity')
    cart_item = CartItem.objects.get(pk=cart_item_id)
    product_detail = ProductDetail.objects.filter(product=cart_item.product, color=cart_item.color, size=cart_item.size).first()
    if int(quantity) > product_detail.quantity:
        return JsonResponse({'status': 'error', 'message': 'Số lượng sản phẩm không đủ'})
    cart_item.quantity = int(quantity)
    cart_item.save()
    if int(quantity) == 0:
        cart_item.delete()
    return JsonResponse({'status': 'success', 'message': 'Cập nhật thành công'})

def delete_cart_item(request):
    cart_item_id = request.POST.get('cart_item_id')
    cart_item = CartItem.objects.get(pk=cart_item_id)
    cart_item.delete()
    return JsonResponse({'success': 'Xóa thành công'})


@api_view(['GET'])
def check_coupon(request):
    coupon_code = request.GET.get('coupon')
    coupon = Coupon.objects.filter(code=coupon_code).order_by('-start_date').first()
    if not coupon:
        return JsonResponse({'status': 'error', 'message': 'Mã giảm giá không hợp lệ'})
    
    now = timezone.now()
    if now < coupon.start_date or now > coupon.end_date:
        return JsonResponse({'status': 'error', 'message': 'Mã giảm giá đã hết hạn'})
    
    total_money = request.GET.get('total_money')
    total_money = float(total_money)
    if total_money < coupon.condition:  
        locale.setlocale(locale.LC_ALL, 'vi_VN.UTF-8')
        condition = locale.format_string('%dđ', int(coupon.condition), grouping=True).replace(',', '.')
        return JsonResponse({'status': 'error', 'message': 'Chưa đủ điều kiện đơn hàng tối thiếu. Đơn hàng tối thiểu là ' + condition})
    
    return JsonResponse({'status': 'success', 'discount': coupon.discount})



def checkout(request):
    if request.method == 'GET':
        return render(request, 'customer/checkout.html')
    
    cart_items = request.POST.getlist('cart_item')
    cart_items = [int(cart_item) for cart_item in cart_items]
    total = request.POST.get('total_money')
    coupon = request.POST.get('coupon')
    discount = request.POST.get('discount')

    cart_items = CartItem.objects.filter(pk__in=cart_items)
    locale.setlocale(locale.LC_ALL, 'vi_VN.UTF-8')
    total = locale.format_string('%dđ', int(total), grouping=True).replace(',', '.')
    context = {
        'cart_items': cart_items,
        'total': total,
        'coupon': coupon,
        'discount': discount
    }
    return render(request, 'customer/checkout.html', context)
    
def add_address(request):
    if request.method == 'POST':
        user = request.user
        form = AddressShippingForm(request.POST)
        if not form.is_valid():
            return JsonResponse({'status': 'error', 'message': 'Thông tin không hợp lệ'})
        receiver = form.cleaned_data['receiver']
        phone = form.cleaned_data['phone']
        address = form.cleaned_data['address']
        address_shipping = AddressShipping(receiver=receiver, phone=phone, address=address, customer=user)
        address_shipping.save()
        data = {
            'status': 'success',
            'result': {
                'id': address_shipping.address_shipping_id,
                'receiver': receiver,
                'phone': phone,
                'address': address
            }
        }
        return JsonResponse(data)


def order(request):
    if request.method == 'POST':
        coupon = request.POST.get('coupon')
        discount = request.POST.get('discount')
        cart_items = request.POST.getlist('cart_item')
        cart_items = CartItem.objects.filter(pk__in=cart_items)
        order_form = OrderForm(request.POST)

        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.customer = request.user
            status =  OrderStatus.objects.get(name='Chờ xác nhận')
            order.status = status
            order.save()
            tracking = Tracking.objects.create(order_status=status, order=order)
            tracking.save()
            coupon = Coupon.objects.filter(code=coupon).order_by('-start_date').first()
            
            if coupon:
                coupon.quantity -= 1
                coupon.save()
            for cart_item in cart_items:
                order_item = OrderItem.objects.create(
                    size=cart_item.size,
                    color=cart_item.color,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price,
                    order=order,
                    product=cart_item.product
                )
                order_item.save()

                product = cart_item.product
                product.total_sold += cart_item.quantity
                product.save()

                product_detail = ProductDetail.objects.filter(product=product, color=cart_item.color, size=cart_item.size).first()
                if product_detail.quantity < cart_item.quantity:
                    raise ValidationError('Sản phẩm đã hết hàng')
                product_detail.quantity -= cart_item.quantity
                product_detail.save()
                
                cart_item.delete()
            return render(request, 'customer/success-order.html')
        else:
            context = {
                'cart_items': cart_items,
                'coupon': coupon,
                'discount': discount,
                'order_form': order_form,   
            }
            return render(request, 'customer/checkout.html', context)
    return redirect('home')


def get_order(request):
    orders = Order.objects.filter(customer=request.user).order_by('-date')
    paginator = Paginator(orders, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'orders' : page_obj.object_list
    }
    return render(request, 'customer/orders.html', context)


def get_order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    order_tracking = Tracking.objects.filter(order=order).annotate(
                            null_date=Case(
                            When(date__isnull=True, then=Value(1)),
                            default=Value(0),
                            output_field=models.IntegerField(),
                        )
                        ).order_by('null_date', 'date')
    context = {
        'order': order,
        'order_tracking': order_tracking
    }
    return render(request, 'customer/order_detail.html', context)

def cancel_order(request):
    order_id = request.GET.get('order_id')
    order = Order.objects.get(pk=order_id)
    order.status = OrderStatus.objects.get(name='Hủy đơn')
    order.save()
    context = {
        'order': order,
    }
    return render(request, 'customer/order_detail.html', context)


def handleFeedback(request):
    if request.method == 'GET':
        order_id = request.GET.get('order_id')
        order = Order.objects.get(pk=order_id)
        context = {
            'order': order
        }
         
    if request.method == 'POST':
        orderitem_id = request.POST.get('order_item_id')
        orderitem = OrderItem.objects.get(pk=orderitem_id)
        product = orderitem.product
        comment = request.POST.get('comment')
        rating = request.POST.get('rating')
        images = request.FILES.getlist('images')
        feedback = Feedback.objects.create(
            comment=comment,
            rating=rating,
            product=product,
            customer=request.user
        )
        feedback.save()
        for image in images:
            feedback_image = FeedbackImage(name=image, feedback=feedback)
            feedback_image.save()
        orderitem.feedback = feedback
        orderitem.save()

        order = orderitem.order
        context = {
            'order': order
        }

    return render(request, 'customer/feedback.html', context)

def getFeedback(request):
    feedbacks = Feedback.objects.filter(customer=request.user).order_by('-date')
    paginator = Paginator(feedbacks, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'feedbacks' : page_obj.object_list
    }
    return render(request, 'customer/list-feedback.html', context)


@api_view(['GET'])
def getFeedbackByProduct(request):
    product_id = request.GET.get('product_id')
    product = Product.objects.get(pk=product_id)
    feedbacks = Feedback.objects.filter(product=product).order_by('-date')
    paginator = PageNumberPagination()
    paginator.page_query_param = 'page'
    paginator.page_size = 5
    result_page = paginator.paginate_queryset(feedbacks, request)
    serializer = FeedbackSerializer(result_page, many=True,context={'request': request})

    respone = paginator.get_paginated_response(serializer.data)
    respone.data['current_page'] = paginator.page.number
    respone.data['total_page'] = paginator.page.paginator.num_pages
    return respone
    
def getCoupon(request):
    coupons = Coupon.objects.filter(start_date__lte=timezone.now(), end_date__gte=timezone.now()).order_by('-start_date')
    paginator = Paginator(coupons, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'coupons' : page_obj.object_list
    }
    return render(request, 'customer/list-coupon.html', context)

def profile(request):
    if request.method == 'GET':
        user = request.user
        last_order =  Order.objects.filter(customer=user).last()
        day_last_order = timezone.now() - last_order.date
        day_last_order = day_last_order.days
        total_order = Order.objects.filter(customer=user).count()
        total_money = Order.objects.filter(customer=user, status__name='Giao hàng thành công').aggregate(total_money=Sum('total'))['total_money']
        context = {
            'user': user,
            'day_last_order': day_last_order,
            'total_order': total_order,
            'total_money': total_money
        }
        return render(request, 'customer/profile.html', context)
    else:
        form = UserForm(request.POST, instance=request.user)
        if not form.is_valid():
            return JsonResponse({'status': 'error', 'message': 'Thông tin không hợp lệ'})
        user = form.save()
        return JsonResponse({'status': 'success', 'message': 'Cập nhật thành công'})
    

def notification(request):
    return render(request, 'customer/notification.html')    

# @login_required(login_url='/login/')
def addProduct(request):
    error = ''
    product_form = ProductForm(request.POST or None)
    product_sale_form = ProductSaleForm(request.POST or None)
    colors = request.POST.getlist('color')
    sizes = request.POST.getlist('size')
    quantities = request.POST.getlist('quantity')
    product_image_form = ProductImageForm(request.POST, request.FILES)
    if product_form.is_valid() and product_sale_form.is_valid() and product_image_form.is_valid():
        product = product_form.save()
        product_sale = ProductSale(price=product_sale_form.cleaned_data['price'], product=product)
        product_sale.save()
        for i in range(len(colors)):
            product_detail = ProductDetail(color=colors[i], size=sizes[i], quantity=quantities[i], product=product)
            product_detail.save()
        images = request.FILES.getlist('name')
        for image in images:
            product_image = ProductImage(name=image, product=product)
            product_image.save()
    else:
        error = 'Bạn cần nhập đầy đủ thông tin'
        print(error)
    return render(request, 'admin/add-product.html',
                  {'product_form': product_form, 'product_sale_form': product_sale_form,
                   'product_image_form': product_image_form, 'error': error})


# @login_required(login_url='/login')
def addCoupon(request):
    error = ''
    if request.method == "POST":
        coupon_form = CouponForm(request.POST)
        if coupon_form.is_valid():
            coupon_form.save()
            coupon_form = Coupon()
        else:
            error = 'Mã giảm giá đã tồn tại trong hệ thống'
    else:
        coupon_form = CouponForm()
    return render(request, 'admin/add-coupon.html', {'coupon_form': coupon_form, 'error': error})


def couponManager(request):
    keyword = request.GET.get('keyword', '')
    coupons = Coupon.objects.filter(code__contains=keyword)
    if request.method == "POST":
        start_date = request.POST.get('start_date', '')
        end_date = request.POST.get('end_date', '')
        if start_date == '' and end_date == '':
            coupons = coupons.objects.all()
        elif end_date == '':
            coupons = coupons.objects.filter(start_date__gte=start_date)
        elif start_date == '':
            coupons = coupons.objects.filter(end_date__lte=end_date)
        else:
            coupons = coupons.objects.filter(Q(start_date__gte=start_date) & Q(end_date__lte=end_date))

    paginator = Paginator(coupons, 20)

    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin/coupons.html', {'page_obj': page_obj})


def productManager(request):
    categories = Category.objects.all()
    keyword = request.GET.get('keyword', '')
    products = Product.objects.filter(name__contains=keyword).annotate(
        total_quantity=Sum('productdetail__quantity'))
    if request.method == "POST":
        category = request.POST.get('category')
        status = request.POST.get('status')
        if category:
            products = products.filter(category__name=category)
        if status:
            if status == 'Còn hàng':
                products = products.filter(total_quantity__gt=0)
            else:
                products = products.filter(total_quantity=0)

    paginator = Paginator(products, 20)

    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin/products.html', {'page_obj': page_obj, 'categories': categories})


def deleteProduct(request, product_id):
    product = Product.objects.get(product_id=product_id)
    product.delete()
    products = Product.objects.all()
    categories = Category.objects.all()

    paginator = Paginator(products, 20)

    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin/products.html', {'page_obj': page_obj, 'categories': categories})
