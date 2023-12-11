from django.contrib import admin
from .models import *
# Register your models here.
    
@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'bank', 'account_number', 'account_name']
    list_filter = ['bank']
    list_editable = ['bank']
    list_per_page = 20

admin.site.register(Bank)
admin.site.register(Reward)
admin.site.register(Task)
admin.site.register(Complaint)
admin.site.register(Query)
@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'site', 'date']
    list_filter = ['site']
    list_editable = ['site']
admin.site.register(Notification)
admin.site.register(GroupChat)
admin.site.register(ChatMessage)