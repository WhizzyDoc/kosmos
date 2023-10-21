from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.

class Profile(models.Model):
    user = models.ForeignKey(User)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    age = models.PositiveIntegerField()
    date_of_entry = models.DateField()
    address = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    reference = models.CharField(max_length=100) #You could remove this if its not necessary
    salary = models.PositiveIntegerField()
    job_role = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)

    # Bank details ... Is it necessary?


class Event(models.Model):
    organizer = models.ForeignKey(Profile, on_delete=models.CASCADE)  # This is the person who created it
    
    title = models.CharField(max_length=256)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=256) # If its online or Live ... should be specified

    def __str__(self):
        return str(self.title)


class News(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.TextField()
    date = models.DateTimeField(default=datetime.now())
    category = models.CharField(choices=()) 
    featured = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return str(self.author) # Cant return post as it may include images...we can strip that sha


class Rewards(models.Model):
    name = models.ForeignKey(User, on_delete=models.PROTECT) 
    reward_type = models.CharField(max_length=100)
    