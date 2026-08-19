from django.contrib import admin

# Register your models here.
from .models import Service, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Service Categories"""
    list_display = ('name', 'is_active', 'workers_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'icon')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def workers_count(self, obj):
        """Show count of workers in this category"""
        return obj.workers.filter(user__is_blocked=False, user__worker_status='APPROVED').count()
    workers_count.short_description = 'Approved Workers'


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Admin interface for creating and managing services"""
    
    list_display = (
        'name',
        'category',
        'price',
        'duration',
        'is_available',
        'workers_available_count',
        'average_rating',
    )

    list_filter = (
        'category',
        'is_available',
        'featured',
        'created_at',
    )

    search_fields = (
        'name',
        'description',
        'category__name',
    )
    
    readonly_fields = ('created_at', 'updated_at', 'average_rating', 'workers_available_count')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'description')
        }),
        ('Pricing & Duration', {
            'fields': ('price', 'duration')
        }),
        ('Location', {
            'fields': ('location',)
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Status & Visibility', {
            'fields': ('is_available', 'featured')
        }),
        ('Statistics', {
            'fields': ('average_rating', 'workers_available_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    ordering = ('category', 'name')
    
    def workers_available_count(self, obj):
        """Show count of workers who offer this service"""
        return obj.workers_for_this_service.count()
    workers_available_count.short_description = 'Available Workers'
    
    def average_rating(self, obj):
        """Show average rating for this service"""
        rating = obj.average_rating
        return f"{rating:.1f} ⭐" if rating > 0 else "No ratings yet"
    average_rating.short_description = 'Average Rating'
