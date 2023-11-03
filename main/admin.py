from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'last_name', 'email', 'id_no', 'position', 'department']
    list_filter = ['department', 'position']
    list_editable = ['department', 'position']
    list_per_page = 20
    
@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'bank', 'account_number', 'account_name']
    list_filter = ['bank']
    list_editable = ['bank']
    list_per_page = 20

admin.site.register(Position)
admin.site.register(Department)
admin.site.register(Bank)
admin.site.register(Reward)
admin.site.register(Task)