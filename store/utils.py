import json
import smtplib
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from django.db.models.query_utils import Q

from .models import *


def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])

    except:
        cart = {}

    print('Cart:', cart)
    items = []
    order = {'get_cart_total': 0, 'get_number_items': 0, 'shipping': False}
    cart_items = order['get_number_items']

    for item in cart:
        # Se for removido um produto da base de dados o carro sem user nao pode desaparecer
        try:
            cart_items += cart[item]['quantity']
            product = Product.objects.get(id=item)
            total = (product.price * cart[item]['quantity'])
            order['get_cart_total'] += total
            order['get_number_items'] += cart[item]['quantity']

            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'image': product.image
                },
                'quantity': cart[item]['quantity'],
                'get_total': total
            }
            items.append(item)
            if product.digital == False:
                order['shipping'] = True
        except:
            pass

    return {'cart_items': cart_items, 'order': order, 'items': items}


def cartData(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cart_items = order.get_number_items
    else:
        cookie_data = cookieCart(request)
        cart_items = cookie_data['cart_items']
        order = cookie_data['order']
        items = cookie_data['items']

    return {'cart_items': cart_items, 'order': order, 'items': items}


def sendEmail(request, order):
    password = "tecnxxjlcwyrmxni"
    if request.user.is_authenticated:
        user = request.user
        email = user.email
    else:
        email = order.customer.email

    mail_items =  order.orderitem_set.all()
    mail_items_str = ""
    for item in mail_items:
        mail_items_str += f"{item.product.name} | quantity: x{item.quantity} | unit price: {item.product.price}\n"

    with smtplib.SMTP("smtp.mail.yahoo.com") as connection:
        connection.starttls()
        connection.login(user="gscmusic_orders@yahoo.com", password=password)
        connection.sendmail(
            from_addr="gscmusic_orders@yahoo.com",
            to_addrs=email,
            msg=f"Subject:Your order nr:{order.transaction_id}\n\n"
                f"Hello {order.customer.name},\n\n"
                f"Your buy is now being processed.\n\n"
                f"Your order items are:\n{mail_items_str}"  
                f"Order total: {float(order.get_cart_total)}"                  
        )

def guest_order(request, data):
    name = data['form']['name']
    email = data['form']['email']
    cookieData = cookieCart(request)
    items = cookieData['items']
    customer, created = Customer.objects.get_or_create(
        email=email,
    )
    customer.name = name
    customer.save()
    order = Order.objects.create(
        customer=customer, complete=False
    )
    for item in items:
        product = Product.objects.get(id=item['product']['id'])
        order_item = OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity']
        )

    return customer, order

def search_products(request):

    search_query = ""
    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')
    products = Product.objects.filter(Q(name__icontains=search_query) |
                                    Q(price__icontains=search_query)
                                    )
    return products, search_query

def pagination_products(request, products, results):
    page = request.GET.get('page')    
    paginator = Paginator(products, results)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        page=1
        products = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
    
    left_index = (int(page)-4)
    if left_index < 1:
        left_index = 1
    right_index = (int(page)+5)
    if right_index > paginator.num_pages:
        right_index = paginator.num_pages+1
    custom_range = range(left_index, right_index)
    return custom_range, products