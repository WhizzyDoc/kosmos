from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['title', 'tagline']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['organizer', 'title', 'date', 'type']
    list_filter = ['type']
    list_editable = ['type']
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