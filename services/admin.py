from django.contrib import admin

# Register your models here.
from .models import FavoriteService, Service, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'icon')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Status', {
            'fields': ('is_active',)
        })
    )


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'category',
        'price',
        'duration',
        'is_available',
    )

    list_filter = (
        'category',
        'is_available',
    )

    search_fields = (
        'name',
        'category',
    )


@admin.register(FavoriteService)
class FavoriteServiceAdmin(admin.ModelAdmin):
    list_display = ('customer', 'service', 'created_at')
    search_fields = ('customer__username', 'service__name')