from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('customer', 'worker', 'booking', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('customer__username', 'worker__username', 'comment')
