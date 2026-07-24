from django.contrib import admin

# Register your models here.
from .models import FavoriteService, Service


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