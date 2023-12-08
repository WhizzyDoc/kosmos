from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from tinymce.models import HTMLField

# Create your models here.
class Plan(models.Model):
    title = models.CharField(max_length=200)
    price = models.BigIntegerField(default=0)
    level = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.title
    class Meta:
        ordering = ['level','id']

class Admins(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="admin", null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(blank=True, null=True, upload_to="admin/image/")
    api_token = models.CharField(max_length=250, null=True, blank=True)
    class Meta:
        ordering = ['first_name']
    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Site(models.Model):
    owner = models.OneToOneField(Admins, on_delete=models.CASCADE, related_name="site", null=True)
    title = models.CharField(max_length=100, null=True, blank=True, verbose_name="Site Title")
    logo = models.ImageField(upload_to="site/logo/", null=True, blank=True)
    about = HTMLField(null=True, blank=True, verbose_name="About Organization")
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Company Phone Number")
    address = models.CharField(max_length=100, null=True, blank=True, verbose_name="Company Address")
    type = models.CharField(max_length=100, null=True, blank=True, verbose_name="Company Type")
    no_of_employees = models.BigIntegerField(null=True, blank=True, verbose_name="Number of Employees")
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, related_name="plan_sites", null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)
    last_modified = models.DateTimeField(auto_now=True, null=True)
    class Meta:
        ordering = ['-created']
    def __str__(self):
        return str(self.title)
    
class Position(models.Model):
    title = models.CharField(max_length=150)
    site = models.ForeignKey(Site, related_name="positions", null=True, blank=True, on_delete=models.CASCADE)
    def __str__(self):
        return f'{self.title}'

class Department(models.Model):
    title = models.CharField(max_length=150)
    site = models.ForeignKey(Site, related_name="departments", null=True, blank=True, on_delete=models.CASCADE)
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
    site = models.ForeignKey(Site, related_name="staff", null=True, blank=True, on_delete=models.CASCADE)
    address = models.CharField(max_length=500, blank=True)
    city = models.CharField(max_length=250, null=True, blank=True)
    state = models.CharField(max_length=250, null=True, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=100, null=True, blank=True)
    position = models.ForeignKey(Position, on_delete=models.DO_NOTHING, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.DO_NOTHING, null=True, blank=True)
    id_no = models.CharField(max_length=15, unique=True, verbose_name="ID Number", blank=True, null=True ) #You could remove this if its not necessary
    salary = models.DecimalField(decimal_places=2, max_digits=15, default=0.00, blank=True, null=True)
    api_token = models.CharField(max_length=250, null=True, blank=True)
    class Meta:
        ordering = ['first_name']
    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Event(models.Model):
    title = models.CharField(max_length=256)
    description = HTMLField(null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=256, null=True, blank=True) # Can serve for both link and venue
    link = models.URLField(null=True, blank=True)
    invitation = models.FileField(upload_to="events/invitations/", null=True, blank=True)
    directions = HTMLField(null=True, blank=True) # optional field
    site = models.ForeignKey(Site, related_name="events", null=True, blank=True, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return str(self.title)
    class Meta:
        ordering = ['-date']

class Meeting(models.Model):
    title = models.CharField(max_length=256)
    description = HTMLField(null=True, blank=True)
    site = models.ForeignKey(Site, related_name="meetings", null=True, blank=True, on_delete=models.CASCADE)
    departments = models.ManyToManyField(Department, related_name="meetings", blank=True)
    members = models.ManyToManyField(Position, related_name="meetings_invited", blank=True)
    attended_by = models.ManyToManyField(Position, related_name="meetings_attended", blank=True)
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
    site = models.ForeignKey(Site, related_name="news", null=True, blank=True, on_delete=models.CASCADE)
    category = models.ForeignKey(NewsCategory, on_delete=models.DO_NOTHING, related_name="news", null=True, blank=True) 
    active = models.BooleanField(default=True, null=True, blank=True)
    verified = models.BooleanField(default=False, null=True, blank=True)
    def __str__(self):
        return self.title
    class Meta:
        ordering = ['-date']

