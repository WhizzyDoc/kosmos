from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from main.models import Profile, Department, Position
from tinymce.models import HTMLField

# Create your models here.
class Site(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True, verbose_name="Site Title")
    tagline = models.CharField(max_length=100, null=True, blank=True, verbose_name="Site Tagline")
    logo = models.ImageField(upload_to="site/logo/", null=True, blank=True)
    about = HTMLField(null=True, blank=True, verbose_name="About Organization")
    objectives = HTMLField(null=True, blank=True)
    mission = HTMLField(null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)
    last_modified = models.DateTimeField(auto_now=True, null=True)
    class Meta:
        ordering = ['-created']
    def __str__(self):
        return str(self.title)
    


class Event(models.Model):
    organizer = models.ForeignKey(Profile, on_delete=models.CASCADE)  # This is the person who created it
    title = models.CharField(max_length=256)
    description = HTMLField(null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=50, choices = (
        ("open", "open"),
        ("invitation", "invitation")
    ))
    location = models.CharField(max_length=256, null=True, blank=True) # Can serve for both link and venue
    link = models.URLField(null=True, blank=True)
    invitation = models.FileField(upload_to="events/invitations/", null=True, blank=True)
    directions = HTMLField(null=True, blank=True) # optional field
    invitees = models.ManyToManyField(Profile, related_name="event_invited")
    attending = models.ManyToManyField(Profile, related_name="event_attending")
    def __str__(self):
        return str(self.title)
    class Meta:
        ordering = ['-date']

class Meeting(models.Model):
    title = models.CharField(max_length=256)
    description = HTMLField(null=True, blank=True)
    departments = models.ManyToManyField(Department, related_name="meetings")
    members = models.ManyToManyField(Position, related_name="meetings_invited")
    attended_by = models.ManyToManyField(Position, related_name="meetings_attended")
    date = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return str(self.title)
    class Meta:
        ordering = ['-date']


class NewsCategory(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    def __str__(self):
        return str(self.title)
    class Meta:
        ordering = ['title']

class News(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    post = HTMLField()
    date = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey(NewsCategory, on_delete=models.DO_NOTHING, related_name="news", choices=()) 
    active = models.BooleanField(default=True)
    verified = models.BooleanField(default=False)
    def __str__(self):
        return self.title
    class Meta:
        ordering = ['-date']

    