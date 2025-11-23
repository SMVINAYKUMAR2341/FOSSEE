"""
API Views for Chemical Equipment Parameter Visualizer
"""
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    if not old_password or not new_password:
        return Response({'error': 'Old and new password required'}, status=400)
    if not user.check_password(old_password):
        return Response({'error': 'Old password is incorrect'}, status=400)
    user.set_password(new_password)
    user.save()
    return Response({'message': 'Password changed successfully'}, status=200)
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.http import FileResponse
from .models import DatasetHistory
from .serializers import (
    DatasetHistorySerializer, 
    DatasetSummarySerializer,
    LoginSerializer,
    UserSerializer
)
from .utils import process_csv_file, generate_pdf_report
from .ml_models import EquipmentMLModel
import pandas as pd
import os
from django.conf import settings
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from django.http import HttpResponse


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    User login endpoint.
    Returns authentication token on successful login.
    
    POST /api/login/
    Body: { "username": "...", "password": "..." }
    """
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(username=username, password=password)
        
        if user:
            # Get or create token for user
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data,
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    User registration endpoint.
    
    POST /api/register/
    Body: { "username": "...", "password": "...", "email": "..." }
    """
    from django.contrib.auth.models import User
    
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    
    if not username or not password:
        return Response({
            'error': 'Username and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(username=username).exists():
        return Response({
            'error': 'Username already exists'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(username=username, password=password, email=email)
    token = Token.objects.create(user=user)
    
    return Response({
        'token': token.key,
        'user': UserSerializer(user).data,
        'message': 'Registration successful'
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    User logout endpoint - deletes auth token.
    
    POST /api/logout/
    """
    request.user.auth_token.delete()
    return Response({
        'message': 'Logout successful'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_csv(request):
    """
    CSV file upload and processing endpoint.
    
    POST /api/upload-csv/
    Body: multipart/form-data with 'file' field
    
    Returns:
        JSON with computed statistics:
        {
            "count": int,
            "avg_flowrate": float,
            "avg_pressure": float,
            "avg_temperature": float,
            "type_distribution": dict
        }
    """
    if 'file' not in request.FILES:
        return Response({
            'error': 'No file provided'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    csv_file = request.FILES['file']
    
    # Validate file extension
    if not csv_file.name.endswith('.csv'):
        return Response({
            'error': 'File must be a CSV'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Process CSV file
        processed_data = process_csv_file(csv_file)
        
        # Save to database
        dataset = DatasetHistory.objects.create(
            filename=csv_file.name,
            user=request.user,
            count=processed_data['count'],
            avg_flowrate=processed_data['avg_flowrate'],
            avg_pressure=processed_data['avg_pressure'],
            avg_temperature=processed_data['avg_temperature'],
            type_distribution=processed_data['type_distribution'],
            raw_data=processed_data['raw_data'],
            equipment_types_count=processed_data.get('equipment_types_count', 0),
            ranges=processed_data.get('ranges', {}),
            type_wise_breakdown=processed_data.get('type_wise_breakdown', {})
        )
        
        # Cleanup old records (keep only last 5)
        DatasetHistory.cleanup_old_records(request.user, keep_last=5)
        
        # Auto-train ML model with all user datasets
        ml_metrics = None
        try:
            # Get all user datasets
            all_datasets = DatasetHistory.objects.filter(user=request.user)
            raw_data = []
            for ds in all_datasets:
                raw_data.extend(ds.raw_data)
            
            if len(raw_data) >= 10:  # Need at least 10 samples
                # Convert to DataFrame
                df = pd.DataFrame(raw_data)
                
                # Train ML model
                ml_model = EquipmentMLModel()
                ml_metrics = ml_model.train(df)

                # Flatten ml_metrics structure so frontend can read expected keys
                # ml_metrics returned from train() has shape: { 'regression': {...}, 'classification': {...} }
                ml_metrics_flat = {}
                regression = ml_metrics.get('regression', {})
                classification = ml_metrics.get('classification', {})

                # Bring regression-level summaries to top-level (training/test/total samples, equipment_types)
                for k in ('training_samples', 'test_samples', 'total_samples', 'equipment_types'):
                    if k in regression:
                        ml_metrics_flat[k] = regression[k]

                # Copy per-parameter metrics under keys expected by frontend
                ml_metrics_flat['flowrate'] = regression.get('flowrate', {})
                ml_metrics_flat['pressure'] = regression.get('pressure', {})
                ml_metrics_flat['temperature'] = regression.get('temperature', {})

                # Include classification metrics as-is
                ml_metrics_flat['classification'] = classification

                # Use flattened metrics for response
                ml_metrics = ml_metrics_flat
                
                # Save model
                model_dir = os.path.join(settings.MEDIA_ROOT, 'ml_models')
                os.makedirs(model_dir, exist_ok=True)
                model_path = os.path.join(model_dir, f'model_user_{request.user.id}.pkl')
                ml_model.save_model(model_path)
                
                # Save ML metrics to the current dataset
                dataset.ml_metrics = ml_metrics_flat
                dataset.save()
        except Exception as ml_error:
            print(f"ML training error: {ml_error}")
            import traceback
            traceback.print_exc()
            # Don't fail the upload if ML training fails
            pass
        
        # Return summary statistics with ML metrics
        response_data = {
            'count': processed_data['count'],
            'avg_flowrate': processed_data['avg_flowrate'],
            'avg_pressure': processed_data['avg_pressure'],
            'avg_temperature': processed_data['avg_temperature'],
            'type_distribution': processed_data['type_distribution'],
            'equipment_types_count': processed_data.get('equipment_types_count', 0),
            'ranges': processed_data.get('ranges', {}),
            'type_wise_breakdown': processed_data.get('type_wise_breakdown', {}),
            'id': dataset.id,
            'message': 'CSV uploaded and processed successfully'
        }
        
        if ml_metrics:
            response_data['ml_metrics'] = ml_metrics
            response_data['ml_trained'] = True
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    except ValueError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dataset_history(request):
    """
    Get history of last 5 CSV uploads for the authenticated user.
    
    GET /api/history/
    
    Returns:
        List of dataset history records (max 5)
    """
    datasets = DatasetHistory.objects.filter(user=request.user).order_by('-uploaded_at')[:5]
    serializer = DatasetHistorySerializer(datasets, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dataset_detail(request, dataset_id):
    """
    Get detailed information about a specific dataset.
    
    GET /api/dataset/<id>/
    """
    try:
        dataset = DatasetHistory.objects.get(id=dataset_id, user=request.user)
        serializer = DatasetHistorySerializer(dataset)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except DatasetHistory.DoesNotExist:
        return Response({
            'error': 'Dataset not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_report(request):
    """
    Generate PDF report for the most recent dataset.
    
    GET /api/generate-report/
    Query params: ?dataset_id=<id> (optional, uses latest if not provided)
    
    Returns:
        PDF file download
    """
    dataset_id = request.query_params.get('dataset_id')
    
    try:
        if dataset_id:
            dataset = DatasetHistory.objects.get(id=dataset_id, user=request.user)
        else:
            # Get most recent dataset
            dataset = DatasetHistory.objects.filter(user=request.user).order_by('-uploaded_at').first()
            
            if not dataset:
                return Response({
                    'error': 'No datasets found'
                }, status=status.HTTP_404_NOT_FOUND)
        
        # Generate PDF
        pdf_buffer = generate_pdf_report(dataset)
        
        # Return as file response
        response = FileResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="equipment_report_{dataset.id}.pdf"'
        
        return response
    
    except DatasetHistory.DoesNotExist:
        return Response({
            'error': 'Dataset not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'Error generating report: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    """
    Get current user information.
    
    GET /api/user/
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def train_model(request):
    """
    Train ML model on dataset
    
    POST /api/train-model/
    Body: { "dataset_id": 1 } (optional, uses all datasets if not provided)
    
    Returns:
    {
        "message": "Model trained successfully",
        "metrics": {
            "flowrate": {"r2_score": 0.95, "mse": 2.3, "mae": 1.2, "rmse": 1.5},
            "pressure": {"r2_score": 0.92, "mse": 5.1, "mae": 1.8, "rmse": 2.3},
            "temperature": {"r2_score": 0.89, "mse": 8.2, "mae": 2.1, "rmse": 2.9},
            "training_samples": 80,
            "test_samples": 20,
            "total_samples": 100,
            "equipment_types": ["Reactor", "Pump", "Heat Exchanger", ...]
        }
    }
    """
    dataset_id = request.data.get('dataset_id')
    
    try:
        # Get dataset(s)
        if dataset_id:
            dataset = DatasetHistory.objects.get(id=dataset_id, user=request.user)
            raw_data = dataset.raw_data
        else:
            # Use all user's datasets
            datasets = DatasetHistory.objects.filter(user=request.user).order_by('-timestamp')
            if not datasets.exists():
                return Response({
                    'error': 'No datasets available for training'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Combine all raw data
            raw_data = []
            for ds in datasets:
                raw_data.extend(ds.raw_data)
        
        if not raw_data or len(raw_data) < 10:
            return Response({
                'error': 'Insufficient data for training. Need at least 10 samples.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Convert to DataFrame
        df = pd.DataFrame(raw_data)
        
        # Train model
        ml_model = EquipmentMLModel()
        metrics = ml_model.train(df)
        
        # Save model
        model_dir = os.path.join(settings.MEDIA_ROOT, 'ml_models')
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, f'model_user_{request.user.id}.pkl')
        ml_model.save_model(model_path)
        
        return Response({
            'message': 'Model trained successfully',
            'metrics': metrics,
            'model_saved': True
        }, status=status.HTTP_200_OK)
        
    except DatasetHistory.DoesNotExist:
        return Response({
            'error': 'Dataset not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'Error training model: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def predict_parameters(request):
    """
    Predict equipment parameters using trained model
    
    POST /api/predict/
    Body: { "equipment_type": "Reactor" }
    
    Returns:
    {
        "equipment_type": "Reactor",
        "predicted_flowrate": 125.5,
        "predicted_pressure": 85.2,
        "predicted_temperature": 350.8
    }
    """
    equipment_type = request.data.get('equipment_type')
    
    if not equipment_type:
        return Response({
            'error': 'equipment_type field is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Load model
        model_path = os.path.join(settings.MEDIA_ROOT, 'ml_models', f'model_user_{request.user.id}.pkl')
        
        if not os.path.exists(model_path):
            return Response({
                'error': 'Model not trained yet. Please train the model first.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        ml_model = EquipmentMLModel()
        ml_model.load_model(model_path)
        
        # Make prediction
        prediction = ml_model.predict(equipment_type)
        
        # Add model accuracy/metrics to the response
        if ml_model.training_history and 'regression' in ml_model.training_history:
            metrics = ml_model.training_history['regression']
            prediction['metrics'] = {
                'flowrate_r2': metrics.get('flowrate', {}).get('r2_score'),
                'pressure_r2': metrics.get('pressure', {}).get('r2_score'),
                'temperature_r2': metrics.get('temperature', {}).get('r2_score'),
                'training_samples': metrics.get('training_samples')
            }

        return Response(prediction, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Error making prediction: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def predict_equipment_type(request):
    """
    Predict equipment type from parameters using classification model
    
    POST /api/predict-type/
    Body: { 
        "flowrate": 125.5,
        "pressure": 85.2,
        "temperature": 350.8
    }
    
    Returns:
    {
        "predicted_type": "Reactor",
        "confidence": 95.8,
        "input_parameters": {
            "flowrate": 125.5,
            "pressure": 85.2,
            "temperature": 350.8
        }
    }
    """
    flowrate = request.data.get('flowrate')
    pressure = request.data.get('pressure')
    temperature = request.data.get('temperature')
    
    if not all([flowrate, pressure, temperature]):
        return Response({
            'error': 'All parameters (flowrate, pressure, temperature) are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Load model
        model_path = os.path.join(settings.MEDIA_ROOT, 'ml_models', f'model_user_{request.user.id}.pkl')
        
        if not os.path.exists(model_path):
            return Response({
                'error': 'Model not trained yet. Please train the model first.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        ml_model = EquipmentMLModel()
        ml_model.load_model(model_path)
        
        # Make prediction
        prediction = ml_model.predict_type(
            float(flowrate),
            float(pressure),
            float(temperature)
        )
        
        return Response(prediction, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Error making prediction: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_feature_importance(request):
    """
    Get feature importance from trained models
    
    GET /api/feature-importance/
    
    Returns:
    {
        "flowrate": {
            "features": ["Type_Encoded"],
            "importance": [1.0]
        },
        "classification": {
            "features": ["Flowrate", "Pressure", "Temperature"],
            "importance": [0.4, 0.35, 0.25]
        }
    }
    """
    try:
        # Load model
        model_path = os.path.join(settings.MEDIA_ROOT, 'ml_models', f'model_user_{request.user.id}.pkl')
        
        if not os.path.exists(model_path):
            return Response({
                'error': 'Model not trained yet. Please train the model first.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        ml_model = EquipmentMLModel()
        ml_model.load_model(model_path)
        
        # Get feature importance
        importance = ml_model.get_feature_importance()
        
        return Response(importance, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Error getting feature importance: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_predictions(request):
    """
    Get predictions for all equipment types in the system.
    
    GET /api/predictions/
    
    Returns:
    {
        "predictions": [
            {
                "equipment_type": "Pump",
                "predicted_flowrate": 150.5,
                "predicted_pressure": 45.2,
                "predicted_temperature": 85.3,
                "confidence_r2": 0.95
            },
            ...
        ],
        "model_metrics": {...}
    }
    """
    try:
        # Load model
        model_path = os.path.join(settings.MEDIA_ROOT, 'ml_models', f'model_user_{request.user.id}.pkl')
        
        if not os.path.exists(model_path):
            return Response({
                'predictions': [],
                'model_metrics': {},
                'total_types': 0,
                'message': 'Model not trained yet. Upload data to train the model.'
            }, status=status.HTTP_200_OK)
        
        ml_model = EquipmentMLModel()
        ml_model.load_model(model_path)
        
        # Get all unique equipment types from user's datasets
        datasets = DatasetHistory.objects.filter(user=request.user)
        equipment_types = set()
        for dataset in datasets:
            for row in dataset.raw_data:
                equipment_types.add(row.get('Type'))
        
        # Generate predictions for all equipment types
        predictions = []
        for eq_type in sorted(equipment_types):
            try:
                pred = ml_model.predict(eq_type)
                predictions.append(pred)
            except Exception as e:
                print(f"Error predicting for {eq_type}: {e}")
        
        # Get model metrics
        model_metrics = {}
        if ml_model.training_history and 'regression' in ml_model.training_history:
            metrics = ml_model.training_history['regression']
            model_metrics = {
                'flowrate_r2': metrics.get('flowrate', {}).get('r2_score'),
                'pressure_r2': metrics.get('pressure', {}).get('r2_score'),
                'temperature_r2': metrics.get('temperature', {}).get('r2_score'),
                'training_samples': metrics.get('training_samples'),
                'total_samples': metrics.get('total_samples')
            }
        
        return Response({
            'predictions': predictions,
            'model_metrics': model_metrics,
            'total_types': len(predictions)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Error generating predictions: {str(e)}',
            'predictions': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_matplotlib_charts(request, dataset_id):
    """
    Generate matplotlib charts for a dataset and return as base64 encoded images.
    
    GET /api/dataset/<id>/charts/
    
    Returns:
    {
        "pie_chart": "base64_encoded_image",
        "bar_chart": "base64_encoded_image",
        "scatter_chart": "base64_encoded_image",
        "line_chart": "base64_encoded_image",
        "comparison_chart": "base64_encoded_image"
    }
    """
    try:
        dataset = DatasetHistory.objects.get(id=dataset_id, user=request.user)
        df = pd.DataFrame(dataset.raw_data)
        
        charts = {}
        
        # 1. Pie Chart - Equipment Type Distribution
        plt.figure(figsize=(10, 8))
        type_counts = df['Type'].value_counts()
        colors = plt.cm.Set3(range(len(type_counts)))
        plt.pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%', 
                colors=colors, startangle=90)
        plt.title('Equipment Type Distribution', fontsize=16, fontweight='bold')
        plt.axis('equal')
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        charts['pie_chart'] = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        # 2. Bar Chart - Type Count
        plt.figure(figsize=(12, 6))
        type_counts.plot(kind='bar', color='skyblue', edgecolor='navy')
        plt.title('Equipment Count by Type', fontsize=16, fontweight='bold')
        plt.xlabel('Equipment Type', fontsize=12)
        plt.ylabel('Count', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        charts['bar_chart'] = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        # 3. Scatter Plot - Flowrate vs Pressure
        plt.figure(figsize=(12, 8))
        types = df['Type'].unique()
        colors = plt.cm.tab10(range(len(types)))
        
        for i, eq_type in enumerate(types):
            type_data = df[df['Type'] == eq_type]
            plt.scatter(type_data['Flowrate'], type_data['Pressure'], 
                       label=eq_type, alpha=0.7, s=100, color=colors[i])
        
        plt.title('Flowrate vs Pressure Correlation', fontsize=16, fontweight='bold')
        plt.xlabel('Flowrate', fontsize=12)
        plt.ylabel('Pressure', fontsize=12)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        charts['scatter_chart'] = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        # 4. Line Chart - Temperature Variation
        plt.figure(figsize=(14, 6))
        plt.plot(range(len(df)), df['Temperature'], marker='o', 
                linestyle='-', linewidth=2, markersize=4, color='coral')
        plt.title('Temperature Variation Across Samples', fontsize=16, fontweight='bold')
        plt.xlabel('Sample Index', fontsize=12)
        plt.ylabel('Temperature (°C)', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        charts['line_chart'] = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        # 5. Comparison Chart - Average Parameters by Type
        plt.figure(figsize=(14, 8))
        
        type_stats = df.groupby('Type').agg({
            'Flowrate': 'mean',
            'Pressure': 'mean',
            'Temperature': 'mean'
        })
        
        x = range(len(type_stats.index))
        width = 0.25
        
        plt.bar([i - width for i in x], type_stats['Flowrate'], width, 
               label='Avg Flowrate', color='skyblue')
        plt.bar(x, type_stats['Pressure'], width, 
               label='Avg Pressure', color='coral')
        plt.bar([i + width for i in x], type_stats['Temperature'], width, 
               label='Avg Temperature', color='lightgreen')
        
        plt.title('Average Parameters by Equipment Type', fontsize=16, fontweight='bold')
        plt.xlabel('Equipment Type', fontsize=12)
        plt.ylabel('Value', fontsize=12)
        plt.xticks(x, type_stats.index, rotation=45, ha='right')
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        charts['comparison_chart'] = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return Response(charts, status=status.HTTP_200_OK)
        
    except DatasetHistory.DoesNotExist:
        return Response({
            'error': 'Dataset not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'Error generating charts: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_dataset(request, dataset_id):
    """
    Delete a specific dataset by ID.
    
    DELETE /api/dataset/<id>/
    
    Returns:
        204 No Content on success
    """
    try:
        dataset = DatasetHistory.objects.get(id=dataset_id, user=request.user)
        dataset.delete()
        return Response({'message': 'Dataset deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
    except DatasetHistory.DoesNotExist:
        return Response({'error': 'Dataset not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'Error deleting dataset: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
