from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from .models import Category, Product, Cart, Order, OrderItem, ProductReview
from accounts.models import User
import random
import string


def random_order_number():
    return 'BT' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


def home(request):
    featured = Product.objects.filter(is_featured=True, is_active=True)[:8]
    new_arrivals = Product.objects.filter(is_new_arrival=True, is_active=True)[:8]
    best_sellers = Product.objects.filter(is_best_seller=True, is_active=True)[:8]
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'featured': featured,
        'new_arrivals': new_arrivals,
        'best_sellers': best_sellers,
        'categories': categories,
    }
    return render(request, 'store/home.html', context)


def shop(request):
    products = Product.objects.filter(is_active=True).order_by('-created_at')
    categories = Category.objects.filter(is_active=True)
    
    category = request.GET.get('category')
    gender = request.GET.get('gender')
    sort = request.GET.get('sort')
    
    if category:
        products = products.filter(category__slug=category)
    if gender:
        products = products.filter(gender=gender)
    if sort:
        if sort == 'price_low':
            products = products.order_by('price')
        elif sort == 'price_high':
            products = products.order_by('-price')
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'categories': categories,
    }
    return render(request, 'store/shop.html', context)


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, is_active=True)
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'category': category, 'products': page_obj}
    return render(request, 'store/category_products.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:4]
    reviews = product.reviews.filter(is_approved=True)
    
    context = {
        'product': product,
        'related_products': related,
        'reviews': reviews,
    }
    return render(request, 'store/product_detail.html', context)


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1)) if request.method == 'POST' else 1
    
    if request.user.is_authenticated:
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity
        cart_item.save()
        messages.success(request, f'{product.name} added to cart!')
    else:
        messages.warning(request, 'Please login to add items to cart.')
    
    return redirect('store:cart')


def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.user.is_authenticated:
        Cart.objects.filter(user=request.user, product=product).delete()
        messages.success(request, f'{product.name} removed from cart.')
    
    return redirect('store:cart')


def cart(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        subtotal = sum((item.get_total for item in cart_items), Decimal('0.00'))
        tax = subtotal * Decimal('0.05')
        shipping = Decimal('50.00') if subtotal < Decimal('500.00') else Decimal('0.00')
        total = subtotal + tax + shipping
        
        context = {
            'cart_items': cart_items,
            'subtotal': subtotal,
            'tax': tax,
            'shipping': shipping,
            'total': total,
        }
        return render(request, 'store/cart.html', context)
    else:
        return render(request, 'store/cart.html')


def update_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if request.user.is_authenticated:
            cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
            else:
                cart_item.delete()
    return redirect('store:cart')


@login_required
def checkout(request):
    if request.method == 'POST':
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items:
            messages.warning(request, 'Your cart is empty!')
            return redirect('store:cart')
        
        subtotal = sum((item.get_total for item in cart_items), Decimal('0.00'))
        tax = subtotal * Decimal('0.05')
        shipping = Decimal('50.00') if subtotal < Decimal('500.00') else Decimal('0.00')
        total = subtotal + tax + shipping
        
        order = Order.objects.create(
            user=request.user,
            order_number=random_order_number(),
            shipping_name=request.POST.get('shipping_name'),
            shipping_phone=request.POST.get('shipping_phone'),
            shipping_address=request.POST.get('shipping_address'),
            shipping_city=request.POST.get('shipping_city'),
            shipping_state=request.POST.get('shipping_state'),
            shipping_zipcode=request.POST.get('shipping_zipcode'),
            subtotal=subtotal,
            tax=tax,
            shipping_cost=shipping,
            total=total,
            payment_method=request.POST.get('payment_method'),
        )
        
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.final_price,
            )
        
        cart_items.delete()
        
        messages.success(request, f'Order {order.order_number} placed successfully!')
        return redirect('store:order_detail', order_number=order.order_number)
    
    cart_items = Cart.objects.filter(user=request.user)
    subtotal = sum((item.get_total for item in cart_items), Decimal('0.00'))
    tax = subtotal * Decimal('0.05')
    shipping = Decimal('50.00') if subtotal < Decimal('500.00') else Decimal('0.00')
    total = subtotal + tax + shipping
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'shipping': shipping,
        'total': total,
    }
    return render(request, 'store/checkout.html', context)


@login_required
def orders(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {'orders': user_orders}
    return render(request, 'store/orders.html', context)


@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    items = order.items.all()
    context = {'order': order, 'items': items}
    return render(request, 'store/order_detail.html', context)


def search(request):
    query = request.GET.get('q')
    products = []
    if query:
        products = Product.objects.filter(name__icontains=query, is_active=True)
    
    context = {'products': products, 'query': query}
    return render(request, 'store/search.html', context)


def faq(request):
    faqs = [
        {'q': 'How long does shipping take?', 'a': 'Shipping typically takes 5-7 business days.'},
        {'q': 'What is the return policy?', 'a': 'Returns accepted within 14 days of delivery.'},
        {'q': 'How can I track my order?', 'a': 'You will receive a tracking link via email once shipped.'},
    ]
    return render(request, 'store/faq.html', {'faqs': faqs})