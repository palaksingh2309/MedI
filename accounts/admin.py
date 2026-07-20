from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'phone_number', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Profile Fields', {'fields': ('profile_picture', 'phone_number', 'date_of_birth')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Profile Fields', {
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'profile_picture')
        }),
    )

