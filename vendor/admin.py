from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.sites import AlreadyRegistered, NotRegistered


User = get_user_model()
try:
    admin.site.unregister(User)
except NotRegistered:
    pass
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'mobile', 'role', 'is_active', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'mobile')
    ordering = ('-created_at',)

    fieldsets = (
        (_('Personal Info'), {
            'fields': (
                'first_name', 'last_name', 'mobile', 'email', 'password',
                'adhar_no', 'pan_no', 'dob',
                'city', 'state', 'country', 'zipcode',
                'address', 'house_or_building', 'road_or_area', 'landmark',
                'district', 'taluka', 'village',
                'role'
            )
        }),
        (_('Driver Info'), {
            'fields': (
                'license_number', 'license_attachment', 'vehicle_number', 'is_driver_available'
            ),
            'classes': ('collapse',),  # Optional: collapsible section
        }),
        (_('Permissions'), {
            'fields': (
                'is_admin', 'is_staff', 'is_active', 'is_superuser', 'groups'
            )
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'created_at')
        }),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2')
            }
        ),
    )

    filter_horizontal = ('groups',)
    readonly_fields = ('created_at',)
