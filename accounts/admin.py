from django.contrib import admin

# Register your models here.

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.core.exceptions import ValidationError
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'role',
            'phone',
            'address',
            'profile_picture',
            'is_verified_worker',
        )


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            form.base_fields['role'].choices = [
                choice for choice in CustomUser.ROLE_CHOICES if choice[0] != 'admin'
            ]
        return form

    def save_model(self, request, obj, form, change):
        if obj.role == 'admin' and not request.user.is_superuser:
            raise ValidationError('Only superusers can create admin accounts.')

        if obj.role == 'worker':
            obj.is_verified_worker = False

        super().save_model(request, obj, form, change)
    list_display = (
        'username',
        'email',
        'role',
        'is_verified_worker',
        'is_staff',
    )

    list_filter = (
        'role',
        'is_verified_worker',
        'is_staff',
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            'Additional Information',
            {
                'fields': (
                    'role',
                    'phone',
                    'address',
                    'profile_picture',
                    'is_verified_worker',
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            'Additional Information',
            {
                'fields': (
                    'role',
                    'phone',
                    'address',
                    'profile_picture',
                    'is_verified_worker',
                )
            },
        ),
    )