
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from customers.forms import UserProfileForm
from orders.models import Order, ProductOrder
from shop.models import Category, Product
from vendor.forms import VendorForm
from shop.forms import ProductItemForm

from account.models import UserProfile
from .models import  Vendor
from django.contrib import messages

from django.contrib.auth.decorators import login_required, user_passes_test
from account.views import check_role_vendor

from django.template.defaultfilters import slugify


from django.db.models import Count , Prefetch
from shop.models import Category

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        print(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        print(profile_form)
        if profile_form.is_valid() :
            profile_form.save()
            messages.success(request, 'Profile updated')
            return redirect('vprofile')
        else:
            print(profile_form.errors)
            
    else:
       
        profile_form = UserProfileForm(instance=profile)
        

    context = {
        'profile_form': profile_form,
        'profile': profile,
    }
    return render(request, 'vendor/vprofile.html', context)


def get_vendor(request):
    try:
        return Vendor.objects.get(user=request.user)
    except Vendor.DoesNotExist:
        return None


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def product_builder(request):
    # Prefetch related products for each category
    categories = Category.objects.annotate(num_projects=Count('products')).prefetch_related(
        Prefetch('products', queryset=Product.objects.all())
    ).order_by('created_at')
    
    for category in categories:
        print(category.products.all())  # Debug: print related products for each category
    
    context = {
        'categories': categories,
    }
    return render(request, 'vendor/product_builder.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_product(request):
    vendor = get_vendor(request)
    print(f"Vendor: {vendor}")  # Debugging line

    if vendor is None:
        messages.error(request, 'You are not authorized to add products.')
        return redirect('some_page')  # Redirect to an appropriate page

    if request.method == 'POST':
        form = ProductItemForm(request.POST, request.FILES)
        if form.is_valid():
            productTitle = form.cleaned_data['product_title']
            product = form.save(commit=False)
            product.vendor = vendor  # Ensure vendor is set
            product.slug = slugify(productTitle)
            try:
                product.save()
                messages.success(request, 'Product Item added successfully!')
                return redirect("product_builder")
            except IntegrityError:
                messages.error(request, 'A product with this title already exists. Please choose a different title.')
                return redirect("add_product")
        else:
            print(form.errors)
    else:
        form = ProductItemForm()
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_product.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def productItem_by_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    productItems = Product.objects.filter(category=category)
    print(productItems.query)  # Print the SQL query
    
    context = {
        'productItems': productItems,
        'category': category,
    }
    return render(request, 'vendor/productItem_by_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_product(request, pk=None):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductItemForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            productTitle = form.cleaned_data['product_title']
            product = form.save(commit=False)
            product.slug = slugify(productTitle)
            form.save()
            messages.success(request, 'Product Item updated successfully!')
            return redirect('product_category', product.category.id)
        else:
            print(form.errors)

    else:
        form = ProductItemForm(instance=product)
        # form.fields['category'].queryset = Category.objects.f
    context = {
        'form': form,
        'product': product,
    }
    return render(request, 'vendor/edit_product.html', context)



@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_product(request, pk=None):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, 'product Item has been deleted successfully!')
    return redirect('product_category', product.category.id)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def my_orders(request):
    orders = Order.objects.filter(is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'vendor/my_orders.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def order_detail(request, order_number):
    try:
        order = get_object_or_404(Order, order_number=order_number)
        ordered_product = ProductOrder.objects.filter(order=order).order_by('-created_at')
        print(ordered_product)
        context = {
            'order': order,
            'ordered_product': ordered_product,
            'subtotal':order.total - order.total_tax, # Assuming this method exists in your Order model
            'tax_data': order.get_total_by_vendor(vendor=request.user)['tax_dict'],
            'grand_total': order.get_total_by_vendor(vendor=request.user)['grand_total'],
        }
        
        print(context)
        return render(request, 'vendor/order_detail.html', context)
    except Order.DoesNotExist:
        return redirect('vendor')  # Redirect to vendor page if order does not exist



def error_404(request, exception):
        data = {}
        return render(request,'404.html', data)

def error_403(request, exception):
        data = {}
        return render(request,'403.html', data)

def error_400(request, exception):
        data = {}
        return render(request,'400.html', data)

def error_500(request,*args, **argv):
        data = {}
        return render(request,'500.html', data)