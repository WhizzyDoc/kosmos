from django.core.management.base import BaseCommand
from main.models import Profile
from rest_framework.authtoken.models import Token

class Command(BaseCommand):
    help = 'Create tokens for existing users'
    
    def handle(self, *args, **options):
        for p in Profile.objects.all():
            Token.objects.get_or_create(user=p)