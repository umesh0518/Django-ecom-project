from .models import Cart, Product, Tax


def get_cart_counter(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.filter(user=request.user)
            if cart_items:
                for cart_item in cart_items:
                    cart_count += cart_item.quantity
            else:
                cart_count = 0
        except:
            cart_count = 0
    return dict(cart_count=cart_count)




from decimal import Decimal, ROUND_HALF_UP

def get_cart_amounts(request):
    subtotal = Decimal('0.00')
    tax = Decimal('0.00')
    grand_total = Decimal('0.00')
    tax_dict = {}

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            try:
                project = Product.objects.get(pk=item.project.id)
                if project.price is not None and item.quantity is not None:
                    subtotal += project.price * item.quantity
            except Product.DoesNotExist:
                continue

        get_tax = Tax.objects.filter(is_active=True)
        for tax_obj in get_tax:
            tax_percentage = tax_obj.tax_percentage
            tax_amount = (tax_percentage / Decimal('100.0')) * subtotal
            tax_amount = tax_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            tax_dict[tax_obj.tax_type] = {str(tax_percentage): tax_amount}
            tax += tax_amount

        grand_total = subtotal + tax

    return {
        'subtotal': subtotal,
        'tax': tax,
        'grand_total': grand_total,
        'tax_dict': tax_dict
    }

