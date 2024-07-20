from django.test import TestCase
from orders.models import Order
from shop.models import Product, Cart, Category
from account.models import User

class ModelsTestCase(TestCase):
    def setUp(self):
        # Create a user and associated user profile
        self.user = User.objects.create_user(
            first_name='Customer',
            last_name='Test',
            username='Customer',
            email='Customer@test.com',
            password='testpassword'
        )
        # Create a category
        self.category = Category.objects.create(category_name='Test Category', description='Test Description')

        # Create a product
        self.product = Product.objects.create(
            product_title='Cloth',
            category=self.category,
            description='A fashionable clth.',
            price=999.99,
            image='product_images/cloth.png',
            is_available=True
        )

    def test_cart_creation(self):
        cart = Cart.objects.create(
            user=self.user,
            project=self.product,
            quantity=1
        )

        # Print the cart details
        print(f"Cart Item: User={cart.user.username}, Product={cart.project.product_title}, Quantity={cart.quantity}")

        self.assertEqual(cart.user, self.user)
        self.assertEqual(cart.project, self.product)
        self.assertEqual(cart.quantity, 1)
        self.assertIsNotNone(cart.created_at)
        self.assertIsNotNone(cart.updated_at)

    def test_product_creation(self):
        # Print the product details
        print(f"Product: Title={self.product.product_title}, Price={self.product.price}, Category={self.product.category.category_name}")

        self.assertEqual(self.product.product_title, 'Cloth')
        self.assertEqual(self.product.price, 999.99)
        self.assertEqual(self.product.category, self.category)
        self.assertTrue(self.product.is_available)
        self.assertIsNotNone(self.product.created_at)
        self.assertIsNotNone(self.product.updated_at)


from django.test import TestCase, Client
from django.urls import reverse

class PlaceOrderViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email="testuser@gmail.com", password='testpassword')
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

        # Create a cart item for the user
        self.cart_item = Cart.objects.create(user=self.user, project=self.product, quantity=1)

    def test_place_order_view_post(self):
        url = reverse('place_order')  # Adjust this if 'place_order' URL name is different

        # Prepare POST data
        post_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '1234567890',
            'email': 'john.doe@example.com',
            'address': '123 Main St',
            'country': 'US',
            'state': 'CA',
            'city': 'San Francisco',
            'payment_method': 'PayPal',  # Adjust as per your form field names
        }

        response = self.client.post(url, post_data, follow=True)  # Follow redirects

        # Print response status and content
        print("Response Status Code:", response.status_code)

        if response.status_code == 200:
            print("PLACE ORDER SUCCESSFUL WITH STATUS CODE :" , response.status_code )
            print(response)
        else:
            # Handle unexpected status codes
            print("Unexpected response status code:", response.status_code)

    def test_place_order_view_get(self):
        url = reverse('place_order')  # Adjust this if 'place_order' URL name is different

        response = self.client.get(url)
