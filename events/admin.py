from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'category', 'status', 'scheduled_date', 'is_featured')
    list_filter = ('status', 'category', 'is_featured', 'scheduled_date')
    search_fields = ('title', 'description', 'creator__username')
    ordering = ('-scheduled_date',)
