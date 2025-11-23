import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import DatasetHistory
from api.ml_models import EquipmentMLModel
import pandas as pd
from django.conf import settings

print("Updating existing datasets with ML metrics...")

users = User.objects.all()

for user in users:
    print(f'\nProcessing user: {user.username}')
    
    # Get all datasets for this user
    datasets = DatasetHistory.objects.filter(user=user)
    
    if not datasets.exists():
        print(f'  No datasets found')
        continue
    
    # Collect all raw data
    raw_data = []
    for ds in datasets:
        if ds.raw_data:
            raw_data.extend(ds.raw_data)
    
    if len(raw_data) < 10:
        print(f'  Not enough data (need 10+ samples, have {len(raw_data)})')
        continue
    
    try:
        # Convert to DataFrame
        df = pd.DataFrame(raw_data)
        
        # Train ML model
        print(f'  Training ML model with {len(raw_data)} samples...')
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
        print(f'  Model saved to: {model_path}')
        
        # Update all datasets with ML metrics
        updated_count = 0
        for ds in datasets:
            ds.ml_metrics = ml_metrics_flat
            ds.save()
            updated_count += 1
        
        print(f'  ✓ Successfully updated {updated_count} datasets with ML metrics')
        print(f'  Metrics: Flowrate R²={ml_metrics_flat["flowrate"].get("r2_score", 0):.3f}, '
              f'Pressure R²={ml_metrics_flat["pressure"].get("r2_score", 0):.3f}, '
              f'Temperature R²={ml_metrics_flat["temperature"].get("r2_score", 0):.3f}')
        
    except Exception as e:
        print(f'  ✗ Error: {e}')
        import traceback
        traceback.print_exc()

print("\n✓ Done! Refresh your browser to see the ML comparison charts.")
