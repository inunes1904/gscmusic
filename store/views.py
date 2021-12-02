import json
from django.db.models.query_utils import Q
from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse
import datetime
from .utils import cookieCart, cartData, pagination_products, search_products, sendEmail, guest_order
from .forms import CreateUserForm, EvaluationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

def store(request):

    cart_data = cartData(request)
    cart_items = cart_data['cart_items']
    products, search_query = search_products(request)  
    custom_range, products = pagination_products(request, products, 6)
    
    context = {'products': products, 'cart_items': cart_items, 'search_query':search_query,  'custom_range': custom_range}
    return render(request, 'store/store.html', context)


def cart(request):

    cart_data = cartData(request)
    items = cart_data['items']
    order = cart_data['order']
    cart_items = cart_data['cart_items']

    context = {
        'items': items,
        'order': order,
        'cart_items': cart_items,
        'shipping': False
    }
    return render(request, 'store/cart.html', context)


def checkout(request):

    data = cartData(request)
    items = data['items']
    order = data['order']
    cart_items = data['cart_items']

    context = {
        'items': items,
        'order': order,
        'cart_items': cart_items
    }
    return render(request, 'store/checkout.html', context)


def update_item(request):
    data = json.loads(request.body)
    product_id = data['productId']
    action = data['action']
    customer = request.user.customer
    product = Product.objects.get(id=product_id)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

    # Se a acao for igual a add adiciona o item a order
    if action == 'add':
        order_item.quantity = (order_item.quantity + 1)
    # Se a acao for igual a remove, remove o item a order
    elif action == 'remove':
        order_item.quantity = (order_item.quantity - 1)
    order_item.save()
    # caso o orderitem tenha quantidade negativa queremos removelo da order
    if order_item.quantity <= 0:
        order_item.delete()
    return JsonResponse('Item was added', safe=False)


def process_order(request):
    # cria o id da transação
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guest_order(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id
    
    # Verifica se alguem com conhecimentos de java não corrompeu o preco do artigo
    if total == float(order.get_cart_total):
        order.complete = True
        sendEmail(request, order)
   
    order.save()
    
    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            zipcode=data['shipping']['zipcode'],
            city=data['shipping']['city'],
            state=data['shipping']['state']
        )

    return JsonResponse('Payment submitted.', safe=False)


def login(request):

    cart_data = cartData(request)
    cart_items = cart_data['cart_items']
    products = Product.objects.all()

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist')

        user=authenticate(username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, 'User logged in!')
            return redirect('store')
        else:
            messages.error(request, 'Username or password incorrect!')

    context = {'products': products, 'cart_items': cart_items}

    return render(request, 'store/login.html', context)

def register(request):

    cart_data = cartData(request)
    cart_items = cart_data['cart_items']
    form = CreateUserForm(request.POST)
    products = Product.objects.all()

    context = {'products': products, 'cart_items': cart_items, 'form':form}

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            
            user = form.cleaned_data.get('username')
            name = form.cleaned_data.get('first_name')
            mail = form.cleaned_data.get('email')
            userIncustomer = User.objects.get(username=user)
            new_customer = Customer.objects.create(user=userIncustomer, email=mail, name=name)
            new_customer.save()
            messages.success(request, "Account was created for " + user)
            return redirect('login')
            

    return render(request, 'store/register.html', context)


def product(request, id):
    cart_data = cartData(request)
    cart_items = cart_data['cart_items']
    
    form = EvaluationForm()
    product = Product.objects.get(id=id)
    evaluations = Evaluation.objects.all().filter(product=product.id)
    if request.method == 'POST':
        form = EvaluationForm(request.POST)
        customer = Customer.objects.get(user=request.user) 
        if form.is_valid():
            product_ev = form.save(commit=False)
            product_ev.product = product
            customer_ev = form.save(commit=False)
            customer_ev.customer = customer
            customer_ev.save()
            product_ev.save()   
    
    stars = product.get_stars    
    context = {'product': product, 'cart_items': cart_items, 'evaluations':evaluations, 'form': form, 'stars':stars}
    return render(request, 'store/product.html', context)


def logout_user(request):
    logout(request)
    messages.info(request, 'User sucessfull logout!')
    return redirect('login')