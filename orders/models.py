import json
from django.db import models
from account.models import User
from shop.models import Product
from vendor.models import Vendor
from decimal import Decimal
import logging

request_object = ''

class Payment(models.Model):
    PAYMENT_METHOD = (
        ('PayPal', 'PayPal'),
        ('RazorPay', 'RazorPay'), # Only for Indian Students.
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100)
    payment_method = models.CharField(choices=PAYMENT_METHOD, max_length=100)
    amount = models.CharField(max_length=10)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_id
    
class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)

    order_number = models.CharField(max_length=20)

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(max_length=50)
    address = models.CharField(max_length=200)
    country = models.CharField(max_length=15, blank=True)
    state = models.CharField(max_length=25, blank=True)
    city = models.CharField(max_length=50)

    total = models.FloatField(blank=True , null = True )
    tax_data = models.JSONField(blank=True, help_text = "Data format: {'tax_type':{'tax_percentage':'tax_amount'}}")
    total_tax = models.FloatField(blank=True , null = True)
    total_data = models.JSONField(blank=True, null=True)

    payment_method = models.CharField(max_length=25)
    status = models.CharField(max_length=15, choices=STATUS, default='New')

    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Concatenate first name and last name

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'


    def get_total_by_vendor(self, vendor):
        subtotal = 0
        tax = 0
        tax_dict = {}

        if self.total_data:
            tax_data = json.loads(self.tax_data)
            data = tax_data.get(str(vendor.id))

            for key, val in data.items():
                val_float = float(val)  # Convert val to float
                subtotal += val_float
                val = val.replace("'", '"')
                val = json.loads(val)
                tax_dict.update(val)

                # Calculate tax
                # {'CGST': {'9.00': '6.03'}, 'SGST': {'7.00': '4.69'}}
                for i in val:
                    for j in val[i]:
                        tax += float(val[i][j])

        grand_total = subtotal + tax  # No need to convert to float again

        context = {
            'subtotal': subtotal,
            'tax_dict': tax_dict,
            'grand_total': grand_total,
        }

        # Debug output
        logging.debug("subtotal: %s", subtotal)
        logging.debug("tax_dict: %s", tax_dict)
        logging.debug("grand_total: %s", grand_total)

        return context
 
class ProductOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()
    amount = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_title

    
