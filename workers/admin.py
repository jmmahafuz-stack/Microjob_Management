from django.contrib import admin

from .models import WorkerProfile


@admin.register(WorkerProfile)
class WorkerProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'skills',
        'experience',
        'training_status',
        'verification_status'
    )
    list_filter = ('training_status', 'verification_status')
    search_fields = ('user__username', 'skills')
