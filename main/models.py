from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django_countries.fields import CountryField

# Create your models here.
class Position(models.Model):
    title = models.CharField(max_length=150)
    def __str__(self):
        return f'{self.title}'

class Department(models.Model):
    title = models.CharField(max_length=150)
    def __str__(self):
        return f'{self.title}'

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profile", null=True, blank=True)
    title = models.CharField(max_length=100, choices=(
        ('Dr', 'Dr'),
        ('Engr', 'Engr'),
        ('Miss', 'Miss'),
        ('Mr', 'Mr'),
        ('Mrs', 'Mrs'),
        ('Prof', 'Prof'),
    ), null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to="profile/image/")
    date_of_birth = models.DateField(blank=True, null=True)
    appointment_date = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=500, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=100, null=True, blank=True)
    position = models.ForeignKey(Position, on_delete=models.DO_NOTHING, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.DO_NOTHING, null=True, blank=True)
    id_no = models.CharField(max_length=15, unique=True, verbose_name="ID Number", blank=True, null=True ) #You could remove this if its not necessary
    salary = models.DecimalField(decimal_places=2, max_digits=15, default=0.00, blank=True, null=True)
    is_premium_user = models.BooleanField(default=False)
    api_token = models.CharField(max_length=250, null=True, blank=True)
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
    bank = models.ForeignKey(Bank, on_delete=models.DO_NOTHING, null=True, blank=True)
    account_number = models.CharField(max_length=15, null=True, blank=True) # Integer field?
    account_name = models.CharField(max_length=200, null=True, blank=True)
    def __str__(self):
        return str(self.user.__str__())



class Reward(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE) 
    description = models.TextField(null=True, blank=True)
    
class Task(models.Model):
    title = models.CharField(max_length=250, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(Profile, related_name="tasks_created", null=True, blank=True, on_delete=models.DO_NOTHING)
    file = models.FileField(upload_to="tasks/files/", null=True, blank=True)
    type = models.CharField(max_length=150, choices=(
        ('general', 'general'),('specific', 'specific')
    ), null=True, blank=True)
    reward = models.ForeignKey(Reward, related_name="tasks", null=True, blank=True, on_delete=models.DO_NOTHING)
    assigned_to = models.ManyToManyField(Profile, related_name="tasks_assigned")
    completed = models.BooleanField(default=False)
    completed_by = models.ManyToManyField(Profile, related_name="tasks_completed")
    date = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return str(self.title)
    class Meta:
        ordering = ['-date']