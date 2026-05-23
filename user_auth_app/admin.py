from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile


class UserProfileAdmin(BaseUserAdmin):
    """Custom admin configuration for the UserProfile model.

    This class overrides the standard Django BaseUserAdmin to adapt the admin
    interface for the custom user model, specifically handling the removal
    of the default username field and integrating the unique email and fullname
    attributes.

    Attributes:
        list_display (tuple): Fields displayed in the admin change list view.
        list_filter (tuple): Fields available for filtering the change list.
        search_fields (tuple): Fields included in the admin search capability.
        ordering (tuple): The default sorting order for the user records.
        filter_horizontal (tuple): ManyToMany fields rendered with a two-box
            horizontal filter interface.
        fieldsets (tuple): Layout organization for the user editing form.
        add_fieldsets (tuple): Layout organization for the user creation form.
    """
    list_display = ('email', 'fullname', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'fullname')
    ordering = ('email',)

    filter_horizontal = ('groups', 'user_permissions')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('fullname',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff',
         'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'fullname', 'password1', 'password2'),
        }),
    )
