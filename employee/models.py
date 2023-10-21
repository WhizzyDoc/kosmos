from django.db import models
from main.models import Profile
from django.utils import timezone

# Create your models here.
class Employee(models.Model):
    user = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="employee")