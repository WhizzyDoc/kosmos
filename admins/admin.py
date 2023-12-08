from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'last_name', 'email', 'id_no', 'position', 'department', 'site']
    list_filter = ['department', 'position', 'site']
    list_editable = ['department', 'position']
    list_per_page = 20

@admin.register(Admins)
class AdminsAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'last_name', 'email', 'phone_number']
    list_per_page = 20

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['title', 'plan']
    list_filter = ['plan']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date']
    list_per_page = 20

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ['title', 'date']
    list_per_page = 20

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['author', 'title', 'category', 'date', 'active', 'verified']
    list_filter = ['active', 'verified', 'category']
    list_editable = ['active', 'verified', 'category']
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 20

admin.site.register(NewsCategory)
admin.site.register(Position)
admin.site.register(Department)
admin.site.register(Plan)