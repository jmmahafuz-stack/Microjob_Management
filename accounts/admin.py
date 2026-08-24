from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from .models import CustomUser
from notifications.utils import NotificationManager
from complaints.models import Complaint
from notifications.models import Notification
from reviews.models import Review

# Keep the admin panel focused on business-critical management screens.
def unregister_if_registered(model):
    if admin.site.is_registered(model):
        admin.site.unregister(model)


unregister_if_registered(Group)
unregister_if_registered(Notification)
unregister_if_registered(Complaint)
unregister_if_registered(Review)


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
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
    ordering = ('email',)

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

        # Check if worker status changed and send notification
        if change and obj.role == 'worker':
            old_obj = CustomUser.objects.get(pk=obj.pk)
            if old_obj.worker_status != obj.worker_status:
                if obj.worker_status == 'APPROVED':
                    NotificationManager.notify_worker_approved(obj)
                elif obj.worker_status == 'REJECTED':
                    NotificationManager.notify_worker_rejected(obj)

        super().save_model(request, obj, form, change)
    
    def worker_status_badge(self, obj):
        """Display worker status with color badge"""
        if obj.role != 'worker':
            return '-'
        
        colors = {
            'PENDING': '#FFC107',   # Yellow
            'APPROVED': '#28A745',  # Green
            'REJECTED': '#DC3545',  # Red
            'BLOCKED': '#6C757D',   # Gray
        }
        color = colors.get(obj.worker_status, '#6C757D')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_worker_status_display()
        )
    worker_status_badge.short_description = 'Worker Status'
    
    def actions_for_workers(self, request, queryset):
        """Custom actions for worker management"""
        # This will be implemented in list view
        pass
    
    actions = ['approve_workers', 'reject_workers', 'block_users', 'unblock_users']
    
    def approve_workers(self, request, queryset):
        """Admin action to approve pending workers"""
        workers = queryset.filter(role='worker', worker_status='PENDING')
        count = 0
        for worker in workers:
            worker.worker_status = 'APPROVED'
            worker.save()
            NotificationManager.notify_worker_approved(worker)
            count += 1
        self.message_user(request, f'{count} worker(s) approved successfully.')
    approve_workers.short_description = "Approve selected workers"
    
    def reject_workers(self, request, queryset):
        """Admin action to reject pending workers"""
        workers = queryset.filter(role='worker', worker_status='PENDING')
        count = 0
        for worker in workers:
            worker.worker_status = 'REJECTED'
            worker.save()
            NotificationManager.notify_worker_rejected(worker)
            count += 1
        self.message_user(request, f'{count} worker(s) rejected.')
    reject_workers.short_description = "Reject selected workers"
    
    def block_users(self, request, queryset):
        """Admin action to block users"""
        count = queryset.update(is_blocked=True)
        self.message_user(request, f'{count} user(s) blocked.')
    block_users.short_description = "Block selected users"
    
    def unblock_users(self, request, queryset):
        """Admin action to unblock users"""
        count = queryset.update(is_blocked=False)
        self.message_user(request, f'{count} user(s) unblocked.')
    unblock_users.short_description = "Unblock selected users"
    
    list_display = (
        'email',
        'role',
        'worker_status_badge',
        'customer_status',
        'is_blocked',
        'created_at',
    )

    list_filter = (
        'role',
        'worker_status',
        'customer_status',
        'is_blocked',
        'is_staff',
        'created_at',
    )

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
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

    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'password1', 'password2')}),
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