from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django_countries.fields import CountryField
from tinymce.models import HTMLField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

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
    city = models.CharField(max_length=250, null=True, blank=True)
    state = models.CharField(max_length=250, null=True, blank=True)
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
    title = models.CharField(max_length=250, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    def __str__(self):
        return str(self.description)
    
class Task(models.Model):
    title = models.CharField(max_length=250, null=True, blank=True)
    description = HTMLField(null=True, blank=True)
    created_by = models.ForeignKey(Profile, related_name="tasks_created", null=True, blank=True, on_delete=models.DO_NOTHING)
    file = models.FileField(upload_to="tasks/files/", null=True, blank=True)
    reward = models.ForeignKey(Reward, related_name="tasks", null=True, blank=True, on_delete=models.DO_NOTHING)
    assigned_to = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name="tasks_assigned", blank=True)
    completed = models.BooleanField(default=False)
    deadline = models.DateTimeField(null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return str(self.title)
    class Meta:
        ordering = ['-date']

class Complaint(models.Model):
    employee = models.ForeignKey(Profile, related_name="complaints", null=True, blank=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=250, null=True, blank=True)
    complaint = models.TextField(null=True, blank=True)
    proposed_solution = models.TextField(null=True, blank=True)
    addressed = models.BooleanField(default=False)
    solution = HTMLField(null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return str(self.title)
    class Meta:
        ordering = ['-date']

class Query(models.Model):
    addressed_to = models.ForeignKey(Profile, related_name="queries", null=True, blank=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=250, null=True, blank=True)
    query = HTMLField(null=True, blank=True)
    addressed = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return str(self.title)
    class Meta:
        ordering = ['-date']


class Log(models.Model):
    user = models.ForeignKey(Profile, related_name='activity_logs', db_index=True, on_delete=models.CASCADE)
    action = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-date']
    def __str__(self):
        return f'{self.action}'

class Notification(models.Model):
    user = models.ForeignKey(Profile, related_name='notifications', db_index=True, on_delete=models.CASCADE)
    verb = models.CharField(max_length=255)
    target_ct = models.ForeignKey(ContentType, blank=True, null=True, related_name='target_obj', on_delete=models.CASCADE)
    target_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    target = GenericForeignKey('target_ct', 'target_id')
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    class Meta:
        ordering = ('-created',)
    def __str__(self):
        return f'{self.user.first_name} {self.verb}'
        
class GroupChat(models.Model):
    title = models.CharField(max_length=250, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="group_chat", blank=True)
    members = models.ManyToManyField(Profile, blank=True, related_name="department_group")
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.title)
    class Meta:
        ordering = ['-created']
        
class ChatMessage(models.Model):
    group = models.ForeignKey(GroupChat, on_delete=models.CASCADE, related_name="chat_messages")
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="chat_sent")
    message = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    seen_by  = models.ManyToManyField(Profile, related_name="chat_seen")
    def __str__(self):
        return f'{self.sender.__str__()}\'s message'
    class Meta:
        ordering = ['date']