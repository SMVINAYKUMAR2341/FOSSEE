"""
Serializers for Chemical Equipment Parameter Visualizer API
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import DatasetHistory


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class DatasetHistorySerializer(serializers.ModelSerializer):
    """Serializer for DatasetHistory model"""
    timestamp = serializers.DateTimeField(source='uploaded_at', read_only=True)
    
    class Meta:
        model = DatasetHistory
        fields = [
            'id',
            'filename',
            'timestamp',
            'count',
            'avg_flowrate',
            'avg_pressure',
            'avg_temperature',
            'type_distribution',
            'ranges',
            'type_wise_breakdown',
            'raw_data',
            'ml_metrics'
        ]
        read_only_fields = ['id', 'timestamp']


class DatasetSummarySerializer(serializers.Serializer):
    """Serializer for CSV upload response"""
    count = serializers.IntegerField()
    avg_flowrate = serializers.FloatField()
    avg_pressure = serializers.FloatField()
    avg_temperature = serializers.FloatField()
    type_distribution = serializers.DictField()


class LoginSerializer(serializers.Serializer):
    """Serializer for login request"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
