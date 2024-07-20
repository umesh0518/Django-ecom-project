from django.test import TestCase, Client
from django.urls import reverse
from account.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.auth import get_user_model
from django.utils import timezone

from orders.models import Order  # Import your Order model
from orders.forms import OrderForm  # Import your OrderForm
from orders.views import place_order  # Import your view function
from shop.models import Cart, Category, Product  # Import your Cart model

class PlaceOrderViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpassword'
        )
        self.client.login(username='testuser', password='testpassword')

        # Create a category
        self.category = Category.objects.create(category_name='Test Category', description='Test Category Description')

        # Create a product
        self.product = Product.objects.create(
            category=self.category,
            vendor=None,
            product_title='Test Product',
            slug='test-product',
            description='Test product description',
            price=100.00,
            image='product_images/test_product.jpg',
            is_available=True
        )

        # Create a sample cart item for the user
        self.cart_item = Cart.objects.create(
            user=self.user,
            project=self.product, # Replace with a valid product instance
            quantity=1,
            created_at=timezone.now()
        )

    def test_place_order_view(self):
        # Setup session and request
        self.client.force_login(self.user)
        session = self.client.session
        session['cart_id'] = self.cart_item.id  # Store cart item ID in session
        session.save()

        # Simulate POST data
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '1234567890',
            'email': 'john.doe@example.com',
            'address': '123 Test St',
            'country': 'US',
            'state': 'CA',
            'city': 'San Francisco',
            'payment_method': 'PayPal',
        }

        try:
            order = Order.objects.create(
                user=self.user,
                first_name='John',
                last_name='Doe',
                phone='1234567890',
                email='john.doe@example.com',
                address='123 Test St',
                country='US',
                state='CA',
                tax_data=13,
                city='San Francisco',
                payment_method='PayPal'
            )
            print("Manual order created:", order)
        except Exception as e:
            print("Error creating manual order:", str(e))

        # Check if the order was created successfully
        response = self.client.post(reverse('place_order'), data, follow=True)  # Assuming you return 200 on success
        print("Response status code:", response.status_code)

        # Check if the order object exists in the database
        orders = Order.objects.filter(user=self.user)
        print("\n-----------------------------------")
        print("User :" , self.user)
        print("Total orders:", orders.count())
        print("\n-----------------------------------")

        self.assertTrue(orders.exists())

        # Check if the order object exists in the database
        self.assertTrue(Order.objects.filter(user=self.user).exists())

        self.client.session.save()
