from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

class CustomUserAdmin(UserAdmin):
    """Define admin model for custom User model with no username field."""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        # (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    search_fields = ("email",)
    list_filter = ("is_active", "is_staff")
    ordering = ("-date_joined",)
    list_display = ("email", "is_active", "is_staff")


admin.site.register(get_user_model(), CustomUserAdmin)
# admin.site.register(CustomUser)

