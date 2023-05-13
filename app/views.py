from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.db.models import F, FloatField, ExpressionWrapper, Sum, Value, CharField
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from .forms import *
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms import formset_factory


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
    top_selling_products = Product.objects.order_by('-total_sold')[:10]

    now = timezone.now()
    top_sale_products = (ProductSale.objects
                         .filter(start_date__lte=now, end_date__gte=now)
                         .select_related('product')
                         .annotate(
        discount_percent=ExpressionWrapper(Coalesce((1 - F('price') / F('product__price')) * 100, 0),
                                           output_field=FloatField()))
                         .order_by('-discount_percent')
                         )[:10]

    top_sale_products = (Product.objects
                         .filter(productsale__start_date__lte=now, productsale__end_date__gte=now).annotate(
        discount_percent=ExpressionWrapper(Coalesce((1 - F('productsale__price') / F('price')) * 100, 0),
                                           output_field=FloatField())).order_by('-discount_percent')
                         )[:10]

    best_selling_product = (Product.objects
                            .filter(orderitem__order__date__month=now.month,
                                    orderitem__order__date__year=now.year).annotate(
        total_sold_month=Sum('orderitem__quantity')).order_by('-total_sold_month')
                            )[:10]
    context = {
        'top_selling_products': top_selling_products,
        'top_sale_products': top_sale_products,
        'best_selling_product': best_selling_product,
        'range': range(10)
    }

    return render(request, 'customer/home.html', context)


def getListProduct(request):
    categories = Category.objects.all()

    category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    rating = request.GET.get('rating')
    sort = request.GET.get('sort')
    top_sale_products = request.GET.get('top_sale_products')
    top_selling_products = request.GET.get('top_selling_products')
    best_selling_product = request.GET.get('best_selling_product')

    products = Product.objects.all()
    if category:
        category = category.split(',')
        products = products.filter(category__id__in=category)

    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:
        products = products.filter(price__lte=max_price)

    if rating:
        products = products.filter(rating__gte=rating)

    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')

    if top_sale_products:
        now = timezone.now()
        products = (products
                    .filter(
            productsale__start_date__lte=now,
            productsale__end_date__gte=now
        ).annotate(
            discount_percent=ExpressionWrapper(Coalesce((1 - F('productsale__price') / F('price')) * 100, 0),
                                               output_field=FloatField())
        ).order_by('-discount_percent')
                    )

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
    products = products.annotate(
        discount_percent=ExpressionWrapper(
            (1 - F('productsale__price') / F('price')) * 100,
            output_field=FloatField()
        )
    )
    context = {}
    context['products'] = products
    context['categories'] = categories
    return render(request, 'list_product.html', context)


def getProductDetail(request, id):
    product = get_object_or_404(Product, pk=id)

    feedbacks = (Feedback.objects.filter(product=product)
                 .order_by('-date')
                 )
    feedback_paginator = Paginator(feedbacks, 5)
    feedback_page = request.GET.get('page')
    feedbacks = feedback_paginator.get_page(feedback_page)

    related_products = (Product.objects
                        .filter(category=product.category)
                        .exclude(pk=product.pk)
                        )[:10]

    context = {
        'product': product,
        'feedbacks': feedbacks,
        'related_products': related_products
    }
    return render(request, 'product_detail.html', context)


def add_to_cart(request, id):
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
        request.session['cart_id'] = cart.id

    cart_item = CartItem.objects.filter(cart=cart, product=product, color=color, size=size).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem.objects.create(cart=cart, product=product, color=color, size=size, quantity=quantity)
    cart_item.save()

    return redirect('cart')


def check_coupon(request):
    coupon_code = request.GET.get('coupon_code')
    coupon = Coupon.objects.filter(code=coupon_code).first()
    if not coupon:
        return JsonResponse({'error': 'Mã giảm giá không hợp lệ'})

    now = timezone.now()
    if now < coupon.start_date or now > coupon.end_date:
        return JsonResponse({'error': 'Mã giảm giá đã hết hạn'})

    total_money = request.GET.get('total_money')
    total_money = float(total_money)
    if total_money < coupon.condition:
        return JsonResponse(
            {'error': 'Chưa đủ điều kiện đơn hàng tối thiếu. Đơn hàng tối thiểu là ' + str(coupon.condition) + 'đ'})

    return JsonResponse({'success': 'Mã giảm giá hợp lệ', 'discount': coupon.discount})


def checkout(request):
    cart_items = request.POST.getlist('cart_item')
    total = request.POST.get('total')
    quantity = request.POST.get('quantity')
    discount = request.POST.get('discount')

    cart_items = CartItem.objects.filter(pk__in=cart_items)

    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'discount': discount
    }
    return render(request, 'checkout.html', context)


def address_shing(request):
    if request.method == 'POST':
        receiver = request.POST.get('receiver')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        address_shipping = AddressShipping(receiver=receiver, phone=phone, address=address)
        address_shipping.save()
        return redirect('checkout')


def payment(request):
    if request.method == 'POST':
        cart_items = request.POST.getlist('cart_item')
        total = request.POST.get('total')
        quantity = request.POST.get('quantity')
        discount = request.POST.get('discount')
        payment_method = request.POST.get('payment_method')
        shipping_method = request.POST.get('shipping_method')
        shipping_price = request.POST.get('shipping_price')
        note = request.POST.get('note')
        address_shipping_id = request.POST.get('address_shipping')
        address_shipping = AddressShipping.objects.get(pk=address_shipping_id)

        order = Order.objects.create(
            total=total,
            discount=discount,
            payment_method=payment_method,
            note=note,
            customer=request.user,
            shipping=shipping_price,
            address_shipping=address_shipping
        )
        order.save()

        cart_items = CartItem.objects.filter(pk__in=cart_items)
        for cart_item in cart_items:
            order_item = OrderItem.objects.create(
                size=cart_item.size,
                color=cart_item.color,
                quantity=cart_item.quantity,
                price=cart_item.product.price,
                customer=request.user,
                order=order,
                product=cart_item.product
            )
            order_item.save()
            cart_item.delete()
    return redirect('home')


def get_order_list(request):
    orders = Order.objects.filter(customer=request.user).order_by('-date')
    context = {
        'orders': orders
    }
    return render(request, 'order_list.html', context)


def get_order_detail(request, id):
    order = get_object_or_404(Order, pk=id)
    context = {
        'order': order
    }
    return render(request, 'order_detail.html', context)


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
