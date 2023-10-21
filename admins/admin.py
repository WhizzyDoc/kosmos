from django.contrib import admin
from .models import *
# Register your models here.

class ProfileAdmin(admin.ModelAdmin):
    list_display = "__all__"

admin.site.register(Profile, ProfileAdmin)