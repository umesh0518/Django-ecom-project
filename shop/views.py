from django.shortcuts import render
from django.db.models import Count
from django.contrib import messages
from django.core.paginator import Paginator
from account.models import User, UserProfile
from shop.forms import ContactForm
from orders.forms import OrderForm
from .context_processors import get_cart_amounts, get_cart_counter
from shop.models import Cart, Category , Product
from django.shortcuts import render, get_object_or_404,redirect
from django.http.response import JsonResponse
from django.contrib.auth.decorators import login_required , user_passes_test
from account.views import check_role_customer

import logging  

logger = logging.getLogger(__name__)
# Create your views here.
def shop_view(request):
    categories = Category.objects.all()
    products = Product.objects.filter(is_available=True)
    category_id = request.GET.get('category')

    if category_id:
        category = get_object_or_404(Category, id=category_id)
        products = products.filter(category=category)

    # Fetch most popular products based on the number of orders
    popular_products = Product.objects.annotate(num_orders=Count('order')).order_by('-num_orders')[:3]

    page = request.GET.get('page')
    paginator = Paginator(products, 9)  # Display 9 products per page
    product_page = paginator.get_page(page)

    context = {
        'categories': categories,
        'product_page': product_page,
        'popular_products': popular_products,  # Add popular products to the context
    }

    return render(request, 'shop/product.html', context)



def product_detail(request, id):
    # Get the current product
    product = get_object_or_404(Product, id=id)

    # Fetch related products based on the same category, excluding the current product
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:3]

    # Fetch most popular products based on the number of orders
    popular_products = Product.objects.annotate(num_orders=Count('order')).order_by('-num_orders')[:3]

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    
    context = {
        'product': [product],
        'related_products': related_products,
        'popular_products': popular_products,
        'cart_items': cart_items,
    }
    return render(request, "shop/prod_detail.html", context)


@login_required
def get_cart_details(request):
    cart_items = Cart.objects.filter(user=request.user)
    product_quantities = {item.project.id: item.quantity for item in cart_items}
    
    return JsonResponse({
        'product_quantities': product_quantities,
    })

def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    context = {
        'cart_items': cart_items,
        'cart_count': cart_count,
    }
    return render(request, 'shop/cart.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_customer)
def add_to_cart(request, product_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Check if the product item exists
            try:
                product = Product.objects.get(id=product_id)
                # Check if the user has already added that product to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, project=product)
                    # Increase the cart quantity
                    chkCart.quantity += 1
                    chkCart.save()
                    return JsonResponse({'status': 'Success', 'message': 'Increased the cart quantity', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
                except:
                    chkCart = Cart.objects.create(user=request.user, project=product, quantity=1)
                    return JsonResponse({'status': 'Success', 'message': 'Added the product to the cart', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'This product does not exist!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})
        
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})


@login_required(login_url='login')
@user_passes_test(check_role_customer)
def decrease_cart(request, product_id):
    logger.info(f'decrease_cart called with product_id: {product_id}')
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                product = get_object_or_404(Product, id=product_id)
                cart_item = get_object_or_404(Cart, user=request.user, project=product)
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                else:
                    cart_item.delete()
                    cart_item.quantity = 0  # Ensure the quantity is set to 0 for the response
                logger.info(f'Cart updated successfully for product_id: {product_id}')
                return JsonResponse({
                    'status': 'Success',
                    'cart_counter': get_cart_counter(request),
                    'qty': cart_item.quantity,
                    'cart_amount': get_cart_amounts(request)
                })
            except Cart.DoesNotExist:
                return JsonResponse({'status': 'Failed', 'message': 'You do not have this item in your cart!'})
            except Product.DoesNotExist:
                return JsonResponse({'status': 'Failed', 'message': 'This product does not exist!'})
            except Exception as e:
                return JsonResponse({'status': 'Failed', 'message': 'An unexpected error occurred'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})


@login_required(login_url='login')
@user_passes_test(check_role_customer)
def delete_cart(request, cart_id):
    logger.info(f'delete_cart called with cart_id: {cart_id}')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            cart_item = get_object_or_404(Cart, user=request.user, id=cart_id)
            cart_item.delete()
            logger.info(f'Cart item deleted successfully with cart_id: {cart_id}')
            return JsonResponse({
                'status': 'Success',
                'message': 'Cart item has been deleted!',
                'cart_counter': get_cart_counter(request),
                'cart_amount': get_cart_amounts(request)
            })
        except Cart.DoesNotExist:
            logger.error(f'Cart item with id {cart_id} does not exist.')
            return JsonResponse({'status': 'Failed', 'message': 'Cart item does not exist!'})
        except Exception as e:
            logger.error(f'Unexpected error in delete_cart: {str(e)}')
            return JsonResponse({'status': 'Failed', 'message': 'An unexpected error occurred'})
    else:
        return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})



@login_required(login_url='login')
@user_passes_test(check_role_customer)
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('shop')
    
    user_profile = UserProfile.objects.get(user=request.user)
    default_values = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'phone': request.user.phone_number,
        'email': request.user.email,
        'address': user_profile.address,
        'country': user_profile.country,
        'state': user_profile.state,
        'city': user_profile.city,
    }
    form = OrderForm(initial=default_values)
    context = {
        'form': form,
        'cart_items': cart_items,
    }
    return render(request,'shop/checkout.html',context )



def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            # Add a success message
            messages.success(request, 'Form submitted successfully!')
            return redirect('contact')  
    else:
        form = ContactForm()
    return render(request, "contact.html", {'form': form})