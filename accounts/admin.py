from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    CustomUser の admin 画面の設定
    """
    list_display = ('email', 'username', 'is_staff', 'is_active', 'is_superuser', 'last_login', 'date_joined')
