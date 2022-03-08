from django.contrib import admin
from apps.user.models import User, Address
# Register your models here.


class UserAdmin(admin.ModelAdmin):
    '''用户'''
    list_display = []

class AddressAdmin(admin.ModelAdmin):
    '''地址'''
    list_display = []


admin.site.register(User)
admin.site.register(Address)