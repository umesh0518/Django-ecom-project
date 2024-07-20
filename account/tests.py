from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import UserProfile , User
import datetime


class UserProfileTestCase(TestCase):

    def test_create_user_and_profile(self):
        # Create a user
        user = User.objects.create_user(
            first_name='Customer',
            last_name='Test',
            username='Customer',
            email='Customer@test.com',
            password='testpassword'
        )

        print("============================================")
        print("User created: ", user)
        print("\n")
        print("User profile created: ", user.userprofile)
        print("============================================")

        # Retrieve the created user's profile
        profile = UserProfile.objects.get(user=user)

        # Assertions to check if the profile was created or updated correctly
        self.assertEqual(profile.user, user)
        self.assertIsNone(profile.address)
        self.assertIsNone(profile.country)
        self.assertIsNone(profile.state)
        self.assertIsNone(profile.city)

        # Test the signal functionality (optional)
        self.assertEqual(profile.user.email, 'Customer@test.com')

        # Check if the profile was created or updated correctly by signal
        self.assertIsNotNone(profile.created_at)
        self.assertIsNotNone(profile.modified_at)
        # self.assertEqual(profile.created_at, profile.modified_at)
        self.assertAlmostEqual(profile.created_at, profile.modified_at, delta=datetime.timedelta(microseconds=10))
