from django.contrib import admin

from accounts.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username', 'is_active', 'is_staff', 'is_superuser', 'last_login')
    list_display_links = ('id', 'email', 'username')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'last_login')
    search_fields = ('email', 'username')
    ordering = ('-id',)
