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
            'city',
            'profile_picture',
            'worker_status',
            'customer_status',
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

        if obj.role == 'worker' and not change:
            obj.worker_status = 'PENDING'

        super().save_model(request, obj, form, change)
    list_display = (
        'username',
        'email',
        'role',
        'worker_status',
        'customer_status',
        'is_blocked',
        'is_staff',
    )

    list_filter = (
        'role',
        'worker_status',
        'customer_status',
        'is_blocked',
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
                    'city',
                    'profile_picture',
                    'worker_status',
                    'customer_status',
                    'is_blocked',
                    'preferred_contact_method',
                    'receive_notifications',
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
                    'city',
                    'profile_picture',
                    'worker_status',
                    'customer_status',
                    'is_blocked',
                    'preferred_contact_method',
                    'receive_notifications',
                )
            },
        ),
    )