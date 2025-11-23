from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import DatasetHistory
from api.ml_models import EquipmentMLModel
import pandas as pd
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Retrain ML models for all users and update datasets with metrics'

    def handle(self, *args, **options):
        users = User.objects.all()
        
        for user in users:
            self.stdout.write(f'Processing user: {user.username}')
            
            # Get all datasets for this user
            datasets = DatasetHistory.objects.filter(user=user)
            
            if not datasets.exists():
                self.stdout.write(f'  No datasets found for {user.username}')
                continue
            
            # Collect all raw data
            raw_data = []
            for ds in datasets:
                raw_data.extend(ds.raw_data)
            
            if len(raw_data) < 10:
                self.stdout.write(f'  Not enough data for {user.username} (need 10+ samples, have {len(raw_data)})')
                continue
            
            try:
                # Convert to DataFrame
                df = pd.DataFrame(raw_data)
                
                # Train ML model
                ml_model = EquipmentMLModel()
                ml_metrics = ml_model.train(df)
                
                # Flatten ml_metrics structure
                ml_metrics_flat = {}
                regression = ml_metrics.get('regression', {})
                classification = ml_metrics.get('classification', {})
                
                # Bring regression-level summaries to top-level
                for k in ('training_samples', 'test_samples', 'total_samples', 'equipment_types'):
                    if k in regression:
                        ml_metrics_flat[k] = regression[k]
                
                # Copy per-parameter metrics
                ml_metrics_flat['flowrate'] = regression.get('flowrate', {})
                ml_metrics_flat['pressure'] = regression.get('pressure', {})
                ml_metrics_flat['temperature'] = regression.get('temperature', {})
                ml_metrics_flat['classification'] = classification
                
                # Save model
                model_dir = os.path.join(settings.MEDIA_ROOT, 'ml_models')
                os.makedirs(model_dir, exist_ok=True)
                model_path = os.path.join(model_dir, f'model_user_{user.id}.pkl')
                ml_model.save_model(model_path)
                
                # Update all datasets with ML metrics
                for ds in datasets:
                    ds.ml_metrics = ml_metrics_flat
                    ds.save()
                
                self.stdout.write(self.style.SUCCESS(
                    f'  ✓ Successfully trained model for {user.username} '
                    f'({len(raw_data)} samples, {len(datasets)} datasets updated)'
                ))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error training model for {user.username}: {e}'))
                import traceback
                traceback.print_exc()
