from django.contrib import admin
from .models import DatasetHistory


@admin.register(DatasetHistory)
class DatasetHistoryAdmin(admin.ModelAdmin):
    """Admin interface for DatasetHistory model"""
    list_display = ['filename', 'user', 'uploaded_at', 'count', 'avg_flowrate', 'avg_pressure', 'avg_temperature']
    list_filter = ['uploaded_at', 'user']
    search_fields = ['filename', 'user__username']
    readonly_fields = ['uploaded_at']
    ordering = ['-uploaded_at']
    
    fieldsets = (
        ('File Information', {
            'fields': ('filename', 'user', 'uploaded_at')
        }),
        ('Statistics', {
            'fields': ('count', 'avg_flowrate', 'avg_pressure', 'avg_temperature', 'type_distribution')
        }),
        ('Raw Data', {
            'fields': ('raw_data',),
            'classes': ('collapse',)
        }),
    )
