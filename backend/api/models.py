"""
Database models for Chemical Equipment Parameter Visualizer
"""
from django.db import models
from django.contrib.auth.models import User


class DatasetHistory(models.Model):
    """
    Model to store CSV upload history and computed statistics.
    Keeps only the last 5 uploads per user.
    """
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='datasets')
    
    # Computed statistics
    count = models.IntegerField(help_text="Total number of equipment entries")
    equipment_types_count = models.IntegerField(default=0, help_text="Number of unique equipment types")
    avg_flowrate = models.FloatField(help_text="Average flowrate across all equipment")
    avg_pressure = models.FloatField(help_text="Average pressure across all equipment")
    avg_temperature = models.FloatField(help_text="Average temperature across all equipment")
    type_distribution = models.JSONField(help_text="Distribution of equipment types")
    ranges = models.JSONField(default=dict, help_text="Min/Max/StdDev ranges for parameters")
    type_wise_breakdown = models.JSONField(default=dict, help_text="Statistics broken down by equipment type")
    ml_metrics = models.JSONField(default=dict, null=True, blank=True, help_text="Machine learning model metrics")
    
    # Store raw data for visualization
    raw_data = models.JSONField(help_text="Raw CSV data in JSON format", null=True, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Dataset History'
        verbose_name_plural = 'Dataset Histories'
    
    def __str__(self):
        return f"{self.filename} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}"
    
    @classmethod
    def cleanup_old_records(cls, user, keep_last=5):
        """
        Delete all but the last 'keep_last' records for a user.
        """
        user_datasets = cls.objects.filter(user=user).order_by('-uploaded_at')
        if user_datasets.count() > keep_last:
            datasets_to_delete = user_datasets[keep_last:]
            for dataset in datasets_to_delete:
                dataset.delete()
