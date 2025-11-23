"""
URL configuration for API endpoints
"""
from django.urls import path
from . import views

urlpatterns = [
    # Authentication endpoints
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('user/', views.user_info, name='user-info'),
    path('change-password/', views.change_password, name='change-password'),
    
    # Dataset endpoints
    path('upload-csv/', views.upload_csv, name='upload-csv'),
    path('history/', views.dataset_history, name='dataset-history'),
    path('dataset/<int:dataset_id>/', views.get_dataset_detail, name='dataset-detail'),
    path('dataset/<int:dataset_id>/delete/', views.delete_dataset, name='delete-dataset'),
    
    # Report generation
    path('generate-report/', views.generate_report, name='generate-report'),
    
    # Machine Learning
    path('train-model/', views.train_model, name='train-model'),
    path('predict/', views.predict_parameters, name='predict'),
    path('predictions/', views.get_all_predictions, name='all-predictions'),
    path('predict-type/', views.predict_equipment_type, name='predict-type'),
    path('feature-importance/', views.get_feature_importance, name='feature-importance'),
]
