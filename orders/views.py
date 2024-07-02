
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.shortcuts import render, redirect
from account.utils import send_notification
from account.views import check_role_customer
from orders.utils import generate_order_number
from shop.models import Cart, Tax
from shop.context_processors import get_cart_amounts
from shop.models import Product
from .forms import OrderForm
from .models import Order, Payment, ProductOrder
import json
from django.contrib.auth.decorators import login_required, user_passes_test

from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.sites.shortcuts import get_current_site


@login_required(login_url='login')
@user_passes_test(check_role_customer)
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by("created_at")
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect("shop")

    subtotal = get_cart_amounts(request)["subtotal"]
    total_tax = get_cart_amounts(request)["tax"]
    grand_total = get_cart_amounts(request)["grand_total"]
    tax_data = get_cart_amounts(request)["tax_dict"]

    if request.method == "POST":

        form = OrderForm(request.POST)
        if form.is_valid():
            print("POST Data:")
            for key, value in request.POST.items():
                print(f"{key}: {value}")
            order = Order()
            order.first_name = form.cleaned_data["first_name"]
            order.last_name = form.cleaned_data["last_name"]

            # Remove country code and keep the last 10 digits of the phone number
            phone_number = form.cleaned_data["phone"]
            form.cleaned_data["phone"] = phone_number
            order.phone = phone_number
            for cart_item in cart_items:
                print("Item in the cart => " , cart_item.project)
                order.pro = cart_item.project
            order.email = form.cleaned_data["email"]
            order.address = form.cleaned_data["address"]
            order.country = form.cleaned_data["country"]
            order.state = form.cleaned_data["state"]
            order.city = form.cleaned_data["city"]
            order.user = request.user
            order.total = grand_total
            order.tax_data = json.dumps(tax_data, cls=DjangoJSONEncoder)
            order.total_tax = total_tax
            order.payment_method = request.POST["payment_method"]
            order.save()
            order_number = generate_order_number(order.id)
            order.order_number = order_number
            order.save()

            # Store the modified order form data and order number in the session
            request.session["order_form_data"] = form.cleaned_data
            request.session["order_number"] = order_number

            # Print session data in the terminal
            print("Session Data:", request.session["order_form_data"])
            print("Order Number:", request.session["order_number"])

            form = OrderForm()
            context = {"order": order, "form": form, "cart_items": cart_items}
            return render(request, "orders/place_order.html", context)
        else:
            print(form.errors)

    return render(request, "orders/place_order.html")


@login_required(login_url='login')
@user_passes_test(check_role_customer)
def payments(request):
        # Check if the request is ajax or not
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        # STORE THE PAYMENT DETAILS IN THE PAYMENT MODEL
        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')

        order = Order.objects.get(user=request.user, order_number=order_number)
        payment = Payment(
            user = request.user,
            transaction_id = transaction_id,
            payment_method = payment_method,
            amount = order.total,
            status = status
        )
        payment.save()

        # UPDATE THE ORDER MODEL
        order.payment = payment
        order.is_ordered = True
        order.save()

        # MOVE THE CART ITEMS TO ORDERED PRODUCT MODEL
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            ordered_product = ProductOrder()
            ordered_product.order = order
            ordered_product.payment = payment
            ordered_product.user = request.user
            ordered_product.product = item.project
            ordered_product.quantity = item.quantity
            ordered_product.price = item.project.price
            ordered_product.amount = item.project.price * item.quantity # total amount
            ordered_product.save()

        # SEND ORDER CONFIRMATION EMAIL TO THE CUSTOMER
        # mail_subject = 'Thank you for ordering with us.'
        # mail_template = 'orders/order_confirmation_email.html'

        # ordered_product = ProductOrder.objects.filter(order=order)
        # customer_subtotal = 0
        # for item in ordered_product:
        #     customer_subtotal += (item.price * item.quantity)
        # tax_data = json.loads(order.tax_data)
        # context = {
        #     'user': request.user,
        #     'order': order,
        #     'to_email': order.email,
        #     'ordered_product': ordered_product,
        #     'domain': get_current_site(request),
        #     'customer_subtotal': customer_subtotal,
        #     'tax_data': tax_data,
        # }
        # send_notification(mail_subject, mail_template, context)
        

        # CLEAR THE CART IF THE PAYMENT IS SUCCESS
        # cart_items.delete() 
        Cart.objects.filter(user=request.user).delete()

        # RETURN BACK TO AJAX WITH THE STATUS SUCCESS OR FAILURE
        response = {
            'order_number': order_number,
            'transaction_id': transaction_id,
        }
        return JsonResponse(response)
    return HttpResponse('Payments view')


def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')

    try:
        order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        ordered_product = ProductOrder.objects.filter(order=order)

        subtotal = 0
        for item in ordered_product:
            subtotal += (item.price * item.quantity)

        tax_data = json.loads(order.tax_data)
        print(tax_data)
        context = {
            'order': order,
            'ordered_product': ordered_product,
            'subtotal': subtotal,
            'tax_data': tax_data,
        }
        return render(request, 'orders/order_complete.html', context)
    except:
        return redirect('index')
    
