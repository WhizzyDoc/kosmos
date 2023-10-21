from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Position(models.Model):
    title = models.CharField(max_length=150)

class Department(models.Model):
    title = models.CharField(max_length=150)

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    age = models.PositiveIntegerField()
    date_of_entry = models.DateField()
    address = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    position = models.ForeignKey(Position, on_delete=models.DO_NOTHING, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.DO_NOTHING, null=True, blank=True)
    id_no = models.PositiveIntegerField(unique=True, verbose_name="ID Number") #You could remove this if its not necessary
    salary = models.DecimalField(decimal_places=2, max_digits=10)
    class Meta:
        ordering = ['first_name']
    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Bank(models.Model):
    bank_name = models.CharField(max_length=100)
    bank_code = models.CharField(max_length=100)
    class Meta:
        ordering = ['bank_name']
    def __str__(self):
        return f'{self.bank_name}'


class BankAccount(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="bank_details")
    bank = models.ForeignKey(Bank, on_delete=models.DO_NOTHING)
    account_number = models.CharField(max_length=15) # Integer field?
    account_name = models.CharField(max_length=200)
    def __str__(self):
        return str(self.user.__str__())



class Rewards(models.Model):
    name = models.ForeignKey(Profile, on_delete=models.PROTECT) 
    reward_type = models.CharField(max_length=100)