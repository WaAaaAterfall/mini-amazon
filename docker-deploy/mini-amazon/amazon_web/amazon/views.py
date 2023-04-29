from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from amazon.models import *
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import UserRegisterForm, UserLoginForm, OrderInfoForm, UserUpdateForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
import socket
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from django import template

register = template.Library()


@register.filter
def multiply(value, arg):
    return value * arg

# send a signal to backend when received a order


def send_signal(o_id):
    print("*****")
    print(o_id)
    o_id = str(o_id)
    HOST = "0.0.0.0"  # "127.0.0.1"  # The server's hostname or IP address
    PORT = 13145
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(o_id.encode('utf8'))
        print(len(o_id.encode('utf8')))
        s.close()


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            # login(request, user)
            messages.success(request, "You have been registered successfully.")
            return redirect("login")
        else:
            messages.error(
                request, "register failed. Invalid information. Please Retype!")
    form = UserRegisterForm()
    return render(request, 'amazon/register.html', {'form': form})


def login_request(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
                return redirect('login')
    else:
        form = UserLoginForm()
    return render(request, 'amazon/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


def home(request):
    # get top 3 best sale product
    best_selling_products = Product.objects.order_by('-sales')[:9]
    return render(request, 'amazon/home.html', {'best_selling_products': best_selling_products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    context = {'product': product}
    return render(request, 'amazon/product_detail.html', context)


@login_required
def add_to_cart(request, product_id):
    quantity = int(request.POST.get('quantity', 1))

    try:
        cart_product = Cart.objects.get(user=request.user, product=product_id)
        cart_product.quantity += quantity
        cart_product.save()
    except Cart.DoesNotExist:
        amazon_user = request.user.amazonuser
        cart_product = Product.objects.get(pk=product_id)
        cart = Cart(user=amazon_user, product=cart_product, quantity=1)
        cart.save()
    messages.success(request, "add to cart successfully.")
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def remove_from_cart(request, product_id):
    cart_product = Cart.objects.get(user=request.user, product=product_id)
    try:
        cart_product.delete()
    except Cart.DoesNotExist:
        pass
    return redirect('cart')


def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    count = cart_items.count()
    subtotal = 0
    Shipping_fee = 0
    for item in cart_items:
        subtotal += item.product.price * item.quantity
    subtotal = round(subtotal, 2)
    Shipping_fee = subtotal * 0.01
    Shipping_fee = round(Shipping_fee, 2)
    tax_addin = (subtotal+Shipping_fee)*(1+0.0698)
    tax_addin = round(tax_addin, 2)
    return render(request, 'amazon/cart.html', {'cart_items': cart_items, 'count': count, 'subtotal': subtotal, 'Shipping_fee': Shipping_fee, 'tax_addin': tax_addin
                                                })


def place_order(request):
    cart_items = Cart.objects.filter(user=request.user)
    if request.method == "POST":
        form = OrderInfoForm(request.POST)
        if form.is_valid():
            for item in cart_items:
                status = 'processing'
                addr_x = request.POST.get('address_x')
                addr_y = request.POST.get('address_y')
                product_id = item.product.id
                product = Product.objects.get(pk=product_id)
                product.sales += 1
                product.save()
                quantity = item.quantity
                order = Order(addr_x=addr_x, addr_y=addr_y,
                              product_id=product_id, count=quantity, user=request.user.amazonuser, ups_account=request.user.amazonuser.ups_account)
                order.save()
                item.delete()
                package_id = order.pk
                # TODO: transfer order_id through socket to backend
                # print(package_id)
                send_signal(package_id)
            send_mail(
                'Congratulations! Your order has been comfirmed',
                'Dear ' + request.user.username +
                ' Thank you 🧡 ',
                'huidan_tan@163.com',
                [request.user.email],
                fail_silently=False,)
            print(request.user.email)
            return render(request, 'amazon/success.html')
        else:
            messages.error(request, "Invalid format.")
            return redirect('place_order')
    else:
        form = OrderInfoForm()

    return render(request, 'amazon/place_order.html', {'form': form})


def base(request):
    cart_items_count = Cart.objects.filter(user=request.user).count()
    return render(request, 'amazon/base.html', {'count': cart_items_count})


def search(request, user_type):
    product_key = Product.objects.filter(description__icontains=user_type)
    # products = product_key
   
    product_category =  Product.objects.filter(category__name__icontains=user_type)
    products = product_key.union(product_category)

  
   
    

    return render(request, 'amazon/search.html', {'products': products})


def user_profile(request):
    # request.user.amazonuser.id
    Recent_Orders = Order.objects.filter(user=request.user.amazonuser)
    return render(request, 'amazon/user_profile.html', {'orders': Recent_Orders, 'user': request.user.amazonuser})


def order_detail(request, package_id):
    order = Order.objects.get(pk=package_id)
    now = datetime.now()
    time_string = now.strftime("%I:%M %p").lower()
    return render(request, 'amazon/order_detail.html', {'order': order, 'time_string': time_string})


def user_edit(request):
    user = request.user.amazonuser
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            # login(request, user)
            messages.success(
                request, "You have update your profile successfully.")
            return redirect("user_profile")
        else:
            messages.error(
                request, "update failed. Invalid information. Please Retype!")
    form = UserUpdateForm()
    return render(request, 'amazon/user_edit.html', {'form': form})


def products(request, category_name):

    if category_name == 'all':
        products = Category.objects.all()

    else:

        products = Category.objects.filter(name=category_name)

    category_names = Category.objects.values_list('name', flat=True).distinct()
    return render(request, 'amazon/products.html', {'products': products, 'category_names': category_names})


def remove_order(request, package_id):
    order = Order.objects.get(user=request.user, package_id=package_id)
    try:
        order.delete()
    except Cart.DoesNotExist:
        pass
    return redirect('user_profile')
