from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from main.models import Profile
from tinymce.models import HTMLField

# Create your models here.

class Admin(models.Model):
    user = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="admin")

class Event(models.Model):
    organizer = models.ForeignKey(Profile, on_delete=models.CASCADE)  # This is the person who created it
    title = models.CharField(max_length=256)
    description = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=50, choices = (
        ("online", "online"),
        ("live", "live")
    ))
    location = models.CharField(max_length=256) # Can serve for both link and venue
    directions = models.TextField() # optional field

    def __str__(self):
        return str(self.title)


class NewsCategory(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

class News(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    post = HTMLField()
    date = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey(NewsCategory, on_delete=models.DO_NOTHING, related_name="news", choices=()) 
    featured = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return str(self.title) # Cant return post as it may include images...we can strip that sha

    