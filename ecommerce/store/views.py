from django.shortcuts import render, redirect, get_object_or_404
from.models import *
from django.http import JsonResponse, HttpResponse
import json
import datetime
from.utils import cookieCart, cartData, guestOrder
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from.forms import CreateUserForm, CategoryForm
from django.contrib import messages



def store(request):

    data = cartData(request)
    cartItems = data['cartItems']
    

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)

def cart(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']


    context = {'items':items, 'order':order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    is_authenticated = request.user.is_authenticated

    context = {'items':items, 'order':order, 'cartItems': cartItems, 'is_authenticated': is_authenticated}
    return render(request, 'store/checkout.html', context)


def updateItem(request):

    data = json.loads(request.body)
    print('Received Data:', data)

    productId = data['productId']
    action = data['action']
    size_id = data.get('sizeId')
    

    print('Action:', action)
    print('ProductId:', productId)
    print('Size', size_id)


    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    size = None

    if product.sizes.exists():
        if size_id:
            size = Size.objects.get(id=size_id)
            print('Size', size.name)
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
        if size:
            orderItem.sizes.add(size)
    else:
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)


    # if product.sizes.exists() and size_id:
    #     size = Size.objects.get(id=size_id)
    #     orderItem, created = OrderItem.objects.get_or_create(order=order, product=product, size=size)
    # else:
    #     orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)


    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
        

    print('Size', size)

    if orderItem.quantity <= 0:
        orderItem.delete()
    else:
        orderItem.save()

    response_data = {
        'message': 'Item was added',
        'item': {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'imageURL': product.imageURL,
            'sizes': size.name if size else None,
            'digital':product.digital,
            'quantity': orderItem.quantity,
            'get_total': product.price * orderItem.quantity,
        }
    }

    return JsonResponse(response_data, safe=False)



def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total):
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer = customer,
            order = order,
            address = data['shipping']['address'],
            city = data['shipping']['city'],
            state = data['shipping']['state'],
            zipcode = data['shipping']['zipcode'],
        )

    return JsonResponse('Payment completed', safe=False)



# views for register /login

def registerPage(request):
    form = CreateUserForm()
    data = cartData(request)
    cartItems = data['cartItems']

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            customer = Customer.objects.create(
                user = user,
                name = user.username,
                email = user.email
            )
            login(request,user)
            messages.success(request, 'Account was created successfully')
            return redirect('store')

    context = {'form': form, 'cartItems': cartItems}
    return render(request, 'store/register.html', context)


def loginPage(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username = username, password = password)

        if user is not None:
            login(request, user)
            return redirect('store')
        else:
            messages.info(request, 'Username OR password is incorrect')
            

    data = cartData(request)
    cartItems = data['cartItems']

    context = {'cartItems': cartItems}
    return render(request, 'store/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')


# view for product details page

def productDetail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    recommended_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'recommended_products': recommended_products,
        **cartData(request),
    }


    return render(request, 'store/product_detail.html', context)

# search option

def search_view(request):

    query = request.GET.get('q')
    results = Product.objects.filter(name__icontains=query)
    data = cartData(request)
    cartItems = data['cartItems']

    context = {'results': results, 'query': query, 'cartItems': cartItems}
    return render(request, 'store/search_results.html', context)

# wishlist

@login_required(login_url='login')
def wishlist_view(request):
    wishlist = Wishlist.objects.get_or_create(user=request.user)[0]
    data = cartData(request)
    cartItems = data['cartItems']

    context = {'wishlist': wishlist, 'cartItems': cartItems}
    return render(request, 'store/wishlist.html', context)


def addToWishlist(request, product_id):
    product = Product.objects.get(pk=product_id)

    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user, products=product).exists()
        if wishlist:
            messages.info(request, 'This product is already in your wishlist.')
            return redirect('store')
    

        wishlist = Wishlist.objects.get_or_create(user=request.user)[0]
        wishlist.products.add(product)
        return redirect('wishlist')
    else:
        messages.info(request, 'Please login to add items to your wishlist.')
        return redirect('login')
   

def removeFromWishlist(request, product_id):
    product = Product.objects.get(pk=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist.products.remove(product)
    return redirect('wishlist')


# dropdown category

def filterByCategory(request):
    data = cartData(request)
    cartItems = data['cartItems']
    
    if request.method == 'GET':
        form = CategoryForm(request.GET)
        if form.is_valid():
            category = form.cleaned_data['category']
            if category:
                products = Product.objects.filter(category=category)
            else:
                products = Product.objects.all()
            return render(request, 'store/filter_category.html', {'products': products, 'form': form, 'cartItems': cartItems})
    else:
        form = CategoryForm()
    
    context = {'form': form}
    return render(request, 'store/filter_category.html', context)