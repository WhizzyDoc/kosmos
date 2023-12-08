from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django_countries.fields import CountryField
from tinymce.models import HTMLField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import uuid
from admins.models import *

# Create your models here.
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
    site = models.ForeignKey(Site, related_name="rewards", null=True, blank=True, on_delete=models.CASCADE)
    
class Task(models.Model):
    title = models.CharField(max_length=250, null=True, blank=True)
    description = HTMLField(null=True, blank=True)
    site = models.ForeignKey(Site, related_name="site_tasks", null=True, blank=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(Admins, related_name="tasks_created", null=True, blank=True, on_delete=models.DO_NOTHING)
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
    site = models.ForeignKey(Site, related_name="site_complaints", null=True, blank=True, on_delete=models.CASCADE)
    proposed_solution = models.TextField(null=True, blank=True)
    addressed = models.BooleanField(default=False)
    solution = HTMLField(null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return str(self.title)
    class Meta:
        ordering = ['-date']
        
class GroupChat(models.Model):
    title = models.CharField(max_length=250, blank=True)
    site = models.ForeignKey(Site, related_name="group_chats", null=True, blank=True, on_delete=models.CASCADE)
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


class Query(models.Model):
    addressed_to = models.ForeignKey(Profile, related_name="queries", null=True, blank=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=250, null=True, blank=True)
    query = HTMLField(null=True, blank=True)
    addressed = models.BooleanField(default=False)
    site = models.ForeignKey(Site, related_name="site_queries", null=True, blank=True, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return str(self.title)
    class Meta:
        ordering = ['-date']

class Log(models.Model):
    user = models.ForeignKey(User, related_name='activity_logs', db_index=True, on_delete=models.CASCADE)
    action = models.TextField()
    site = models.ForeignKey(Site, related_name="logs", null=True, blank=True, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-date']
    def __str__(self):
        return f'{self.action}'


class Notification(models.Model):
    user = models.ForeignKey(Admins, related_name='notifications', db_index=True, on_delete=models.CASCADE)
    verb = models.CharField(max_length=255)
    site = models.ForeignKey(Site, related_name="site_notifications", null=True, blank=True, on_delete=models.CASCADE)
    target_ct = models.ForeignKey(ContentType, blank=True, null=True, related_name='target_obj', on_delete=models.CASCADE)
    target_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    target = GenericForeignKey('target_ct', 'target_id')
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    class Meta:
        ordering = ('-created',)
    def __str__(self):
        return f'{self.user.first_name} {self.verb}'

class ForgottenPassword(models.Model):
    user = models.ForeignKey(Profile, related_name = "forgotten_password", on_delete = models.CASCADE)
    temporary_password = models.CharField(max_length = 100)

    def __str__(self):
        return str(self.user)
