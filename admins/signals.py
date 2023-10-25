from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from main.models import Profile
"""
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # create a token for the user
        token, _ = Token.objects.get_or_create(user=instance)
        Profile.objects.create(user=instance, api_token=token)
"""