
import json
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required, user_passes_test
from account.views import check_role_customer
from . forms import UserProfileForm
from account.models import UserProfile
from django.contrib import messages
from orders.models import Order, ProductOrder
from account.models import User
from shop.models import Product

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def cprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        print(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        print(profile_form)
        if profile_form.is_valid() :
            profile_form.save()
            messages.success(request, 'Profile updated')
            return redirect('cprofile')
        else:
            print(profile_form.errors)
            
    else:
       
        profile_form = UserProfileForm(instance=profile)
        

    context = {
        'profile_form': profile_form,
        'profile': profile,
    }
    return render(request, 'customers/cprofile.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')

    context = {
        'orders': orders
    }
    return render(request, 'customers/my_orders.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def order_detail(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_product = ProductOrder.objects.filter(order=order).order_by('-created_at')
        subtotal = 0
        for item in ordered_product:
            subtotal += (item.price * item.quantity)
        tax_data = json.loads(order.tax_data) if order.tax_data else {}
        context = {
            'order': order,
            'ordered_product': ordered_product,
            'subtotal': subtotal,
            'tax_data': tax_data,
        }
    except json.JSONDecodeError as e:
        print(f"Error decoding tax_data: {str(e)}")
    
    return render(request, 'customers/order_detail.html', context)
