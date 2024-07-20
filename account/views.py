from datetime import date, datetime, timezone
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import message
from django.http import JsonResponse
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.utils.http import urlsafe_base64_decode

from shop.models import Product
from django.db.models import Sum , Avg
# from vendor.forms import VendorForm
from .forms import  UserForm , CustomPasswordChangeForm
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import update_session_auth_hash
from .models import User, UserProfile, VisitorCount

from django.contrib import messages, auth
from .utils import detectUser, get_past_7_days_sales, send_verification_email
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied

from vendor.models import Vendor
from orders.models import Order, ProductOrder
import datetime

@login_required(login_url='login')
def myAccount(request):
    user = request.user
    if user.is_authenticated:
        redirect_url = detectUser(user)
        if redirect_url:
            return redirect(redirect_url)
        else:
            messages.error(request, 'Unable to determine dashboard for the user.')
            return redirect('account:login')
    else:
        messages.error(request, 'You need to log in to access your account.')
        return redirect('account:login')
    

# Restrict the vendor from accessing the customer page
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


# Restrict the customer from accessing the vendor page
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied


def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('dashboard')
    elif request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # Create the user using create_user method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name,username=username, email=email, password=password)
            user.role = User.CUSTOMER
            user.is_active = True
            user.save()

            messages.success(request, 'Your account has been registered sucessfully!')
            return redirect('registerUser')
        else:
            print('invalid form')
            print(form.errors)
    else:
        form = UserForm()
    context = {
        'form': form,
    }
    return render(request, 'account/registerUser.html', context)


def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    elif request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # Create the user using create_user method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name,username=username, email=email, password=password)
            user.role = User.VENDOR
            user.is_active = True
            user.save()
            
            user_profile = UserProfile.objects.get(user=user)
            Vendor.objects.create(user=user, user_profile=user_profile, vendor_name=f'{first_name} {last_name}')

            messages.success(request, 'Your account has been registered successfully!')
            return redirect('login')
        else:
            print('invalid form')
            print(form.errors)
    else:
        form = UserForm()
    context = {
        'form': form,
    }
    return render(request, 'account/registerVendor.html', context)



def activate(request, uidb64, token):
    # Activate the user by setting the is_active status to True
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulation! Your account is activated.')
        return redirect('myAccount')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('myAccount')
        

def login(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        print(user)
        if user is not None and user.is_active:
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('myAccount')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'account/login.html')


def logout(request):
    auth.logout(request)
    messages.info(request, 'You are logged out.')
    return redirect('login')



@login_required(login_url='login')
@user_passes_test(check_role_customer)
def custDashboard(request):
    user = request.user
    orders = Order.objects.filter(user=user)
    # Get the current month and year
    current_date = date.today()
    current_month = current_date.month
    current_year = current_date.year

    # Filter orders for the current month and for the specified user
    current_month_orders = Order.objects.filter(user=user, created_at__month=current_month, created_at__year=current_year)
    average_value = 0
    if orders.exists():
        average_value = orders.aggregate(avg_value=Avg('total'))['avg_value']
        

    orders_count = orders.count()
    total_investment = orders.aggregate(Sum('total'))['total__sum'] or 0
    
    ordered_product = ProductOrder.objects.filter(user=user)
    recent_orders = ProductOrder.objects.filter(user=request.user).order_by('-created_at')[:7]

    context = {
        'user': user,
        'orders_count': orders_count,
        'recent_orders': recent_orders,
        'total_investment': total_investment,
        'ordered_product': ordered_product,
        'average_value': average_value,
        'current_month_orders': current_month_orders.count,
    }
    return render(request, 'account/custDashboard.html' , context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    vendor = request.user
    # Fetch total orders and total revenue for the vendor
    orders = Order.objects.filter( is_ordered=True)
    orders_count = orders.count()
    total_revenue = sum(order.total for order in orders)
    total_revenue = round(total_revenue , 2)

    # Fetch active projects
    products = Product.objects.all()
    product_count = products.count()

    # Get visitor count
    try:
        visitor_counts = VisitorCount.objects.all()
    except VisitorCount.DoesNotExist:
        visitor_counts = None

    if visitor_counts:
        visitor_count = visitor_counts
    else:
        visitor_count = 0  # or handle the case when the visitor count does not exist


    sales_data = get_past_7_days_sales()
    dates = [data['date'] for data in sales_data]
    total_sales = [data['total_sales'] for data in sales_data]

    recent_orders = Order.objects.order_by('-created_at')[:5]

    context = {
        'orders_count': orders_count,
        'total_revenue': total_revenue,
        'products': products,
        'product_count': product_count ,
        'visitor_count': visitor_count.count,
        'dates': dates,
        'total_sales': total_sales,
        'recent_orders': recent_orders
    }

    return render(request, 'account/vendordashboard.html' , context)


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # send reset password email
            mail_subject = 'Reset Your Password'
            email_template = 'account/emails/reset_password_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Password reset link has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgot_password')
    return render(request, 'account/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, 'Please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('myAccount')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('reset_password')
    return render(request, 'account/reset_password.html')


@login_required(login_url='login')
@user_passes_test(check_role_customer)
def user_change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Update session
            messages.success(
                request, 'Your password was successfully updated!')
            logout(request)  # Log out the user

            if user.role == 2:
                return redirect('custDashboard')
    else:
        # Pass user=request.user to initialize the form with the user's data
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, 'account/change_password.html', {'form': form})

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendor_change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Update session
            messages.success(
                request, 'Your password was successfully updated!')
            logout(request)  # Log out the user

            if user.role == 1:
                return redirect('vendorDashboard')
    else:
        # Pass user=request.user to initialize the form with the user's data
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, 'account/change_password.html', {'form': form})


