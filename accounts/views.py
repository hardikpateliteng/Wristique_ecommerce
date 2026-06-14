from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import User

User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('store:home')
        else:
            messages.error(request, 'Invalid email or password!')
    
    return render(request, 'store/login.html')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        phone = request.POST.get('phone')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match!')
            return redirect('accounts:register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return redirect('accounts:register')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            phone=phone,
        )
        
        login(request, user)
        messages.success(request, 'Account created successfully!')
        return redirect('store:home')
    
    return render(request, 'store/register.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('store:home')


@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        user.username = request.POST.get('username')
        user.phone = request.POST.get('phone')
        user.save()
        messages.success(request, 'Profile updated!')
        return redirect('accounts:profile')
    from store.models import Order
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {'orders': orders}
    return render(request, 'store/profile.html', context)


@login_required
def edit_profile(request):
    return render(request, 'store/profile.html')


@login_required
def my_orders(request):
    from store.models import Order
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {'orders': orders}
    return render(request, 'store/orders.html', context)