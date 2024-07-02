from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from vendor.models import Vendor

@receiver(post_save, sender=User)
def create_vendor(sender, instance, created, **kwargs):
    if created and instance.role == User.VENDOR:
        Vendor.objects.create(user=instance, user_profile=instance.userprofile)