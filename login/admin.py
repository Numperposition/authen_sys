from django.contrib import admin
from login.models import userInfo

# Register your models here.

class UserInfoAdmin(admin.ModelAdmin):  # extends from ModelAdmin
    list_display = ['user_name', 'user_email', 'token']

# class UserTokenAdmin(admin.ModelAdmin):
#     list_display = ['user', 'token']

admin.site.register(userInfo, UserInfoAdmin)
#admin.site.register(userToken, UserTokenAdmin)