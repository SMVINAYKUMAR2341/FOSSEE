"""
Machine Learning models for equipment parameter prediction
Enhanced with multiple model comparison and advanced metrics
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.svm import SVC, SVR
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    mean_squared_error, r2_score, mean_absolute_error,
    accuracy_score, classification_report, confusion_matrix
)
from scipy import stats
import pickle
import os
import time
from django.conf import settings


class EquipmentMLModel:
    """
    Advanced Machine Learning model for equipment parameter prediction
    Supports both Classification (equipment type) and Regression (parameters)
    """
    
    def __init__(self):
        # Regression models for parameter prediction
        self.model_flowrate = None
        self.model_pressure = None
        self.model_temperature = None
        
        # Classification model for equipment type prediction
        self.classifier_model = None
        
        # Preprocessing
        self.label_encoder = LabelEncoder()
        self.scaler_regression = StandardScaler()
        self.scaler_classification = StandardScaler()
        
        self.feature_names = []
        self.is_trained = False
        self.training_history = {
            'regression': {},
            'classification': {}
        }
        
    
    def clean_data(self, df):
        """
        Clean data by handling missing values and outliers
        
        Args:
            df: DataFrame with equipment data
            
        Returns:
            Cleaned DataFrame
        """
        df_clean = df.copy()
        
        # Handle missing values
        numeric_cols = ['Flowrate', 'Pressure', 'Temperature']
        for col in numeric_cols:
            if df_clean[col].isnull().any():
                df_clean[col].fillna(df_clean[col].median(), inplace=True)
        
        # Remove outliers using Z-score (threshold = 3)
        z_scores = np.abs(stats.zscore(df_clean[numeric_cols]))
        df_clean = df_clean[(z_scores < 3).all(axis=1)]
        
        return df_clean
    
    def prepare_data(self, df):
        """
        Prepare data for training
        
        Args:
            df: DataFrame with equipment data
            
        Returns:
            X, y_flowrate, y_pressure, y_temperature
        """
        # Clean data first
        data = self.clean_data(df)
        
        # Encode equipment type
        data['Type_Encoded'] = self.label_encoder.fit_transform(data['Type'])
        
        # Create features
        X = data[['Type_Encoded']].copy()
        
        # Target variables
        y_flowrate = data['Flowrate']
        y_pressure = data['Pressure']
        y_temperature = data['Temperature']
        
        self.feature_names = ['Type_Encoded']
        
        return X, y_flowrate, y_pressure, y_temperature
    
    def train_regression_models(self, df):
        """
        Train multiple regression models and select the best
        
        Args:
            df: DataFrame with equipment data
            
        Returns:
            dict: Training metrics for all models
        """
        # Prepare data
        X, y_flowrate, y_pressure, y_temperature = self.prepare_data(df)
        
        # Split data
        X_train, X_test, y_flow_train, y_flow_test = train_test_split(
            X, y_flowrate, test_size=0.2, random_state=42
        )
        _, _, y_pres_train, y_pres_test = train_test_split(
            X, y_pressure, test_size=0.2, random_state=42
        )
        _, _, y_temp_train, y_temp_test = train_test_split(
            X, y_temperature, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler_regression.fit_transform(X_train)
        X_test_scaled = self.scaler_regression.transform(X_test)
        
        # Train multiple models for each parameter
        models_to_test = {
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10),
            'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'Linear Regression': LinearRegression()
        }
        
        results = {}
        
        # Train for Flowrate
        best_flow_score = -np.inf
        for name, model in models_to_test.items():
            start = time.time()
            model.fit(X_train_scaled, y_flow_train)
            pred = model.predict(X_test_scaled)
            r2 = r2_score(y_flow_test, pred)
            
            if r2 > best_flow_score:
                best_flow_score = r2
                self.model_flowrate = model
        
        # Train for Pressure
        best_pres_score = -np.inf
        for name, model in models_to_test.items():
            model_copy = type(model)(**model.get_params() if hasattr(model, 'get_params') else {})
            model_copy.fit(X_train_scaled, y_pres_train)
            pred = model_copy.predict(X_test_scaled)
            r2 = r2_score(y_pres_test, pred)
            
            if r2 > best_pres_score:
                best_pres_score = r2
                self.model_pressure = model_copy
        
        # Train for Temperature
        best_temp_score = -np.inf
        for name, model in models_to_test.items():
            model_copy = type(model)(**model.get_params() if hasattr(model, 'get_params') else {})
            model_copy.fit(X_train_scaled, y_temp_train)
            pred = model_copy.predict(X_test_scaled)
            r2 = r2_score(y_temp_test, pred)
            
            if r2 > best_temp_score:
                best_temp_score = r2
                self.model_temperature = model_copy
        
        # Evaluate best models
        flow_pred = self.model_flowrate.predict(X_test_scaled)
        pres_pred = self.model_pressure.predict(X_test_scaled)
        temp_pred = self.model_temperature.predict(X_test_scaled)
        
        metrics = {
            'flowrate': {
                'r2_score': float(r2_score(y_flow_test, flow_pred)),
                'mse': float(mean_squared_error(y_flow_test, flow_pred)),
                'mae': float(mean_absolute_error(y_flow_test, flow_pred)),
                'rmse': float(np.sqrt(mean_squared_error(y_flow_test, flow_pred)))
            },
            'pressure': {
                'r2_score': float(r2_score(y_pres_test, pres_pred)),
                'mse': float(mean_squared_error(y_pres_test, pres_pred)),
                'mae': float(mean_absolute_error(y_pres_test, pres_pred)),
                'rmse': float(np.sqrt(mean_squared_error(y_pres_test, pres_pred)))
            },
            'temperature': {
                'r2_score': float(r2_score(y_temp_test, temp_pred)),
                'mse': float(mean_squared_error(y_temp_test, temp_pred)),
                'mae': float(mean_absolute_error(y_temp_test, temp_pred)),
                'rmse': float(np.sqrt(mean_squared_error(y_temp_test, temp_pred)))
            },
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'total_samples': len(X),
            'equipment_types': self.label_encoder.classes_.tolist()
        }
        
        self.training_history['regression'] = metrics
        return metrics
    
    def train_classification_model(self, df):
        """
        Train classification model to predict equipment type
        
        Args:
            df: DataFrame with equipment data
            
        Returns:
            dict: Classification metrics
        """
        # Clean data
        data = self.clean_data(df)
        
        # Features and target
        X = data[['Flowrate', 'Pressure', 'Temperature']]
        y = self.label_encoder.fit_transform(data['Type'])
        
        # Check if stratification is possible (all classes must have at least 2 samples)
        unique, counts = np.unique(y, return_counts=True)
        can_stratify = all(count >= 2 for count in counts)
        
        # Split data
        if can_stratify:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
        else:
            # Use simple split without stratification
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
        
        # Scale features
        X_train_scaled = self.scaler_classification.fit_transform(X_train)
        X_test_scaled = self.scaler_classification.transform(X_test)
        
        # Train Random Forest Classifier (best for this use case)
        self.classifier_model = RandomForestClassifier(
            n_estimators=100, 
            random_state=42, 
            max_depth=10
        )
        self.classifier_model.fit(X_train_scaled, y_train)
        
        # Predictions
        y_pred = self.classifier_model.predict(X_test_scaled)
        
        # Metrics
        accuracy = accuracy_score(y_test, y_pred)
        
        classification_metrics = {
            'accuracy': float(accuracy),
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'equipment_types': self.label_encoder.classes_.tolist(),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
        }
        
        self.training_history['classification'] = classification_metrics
        return classification_metrics
    
    def train(self, df):
        """
        Train both regression and classification models
        
        Args:
            df: DataFrame with equipment data
            
        Returns:
            dict: Combined training metrics
        """
        # Train regression models
        regression_metrics = self.train_regression_models(df)
        
        # Train classification model
        classification_metrics = self.train_classification_model(df)
        
        self.is_trained = True
        
        # Combine metrics
        return {
            'regression': regression_metrics,
            'classification': classification_metrics,
            'status': 'success'
        }
    
    def predict(self, equipment_type):
        """
        Predict parameters for a given equipment type (regression)
        
        Args:
            equipment_type: Type of equipment
            
        Returns:
            dict: Predicted flowrate, pressure, temperature
        """
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        
        # Encode the equipment type
        try:
            type_encoded = self.label_encoder.transform([equipment_type])[0]
        except ValueError:
            # If type not seen during training, use mean prediction
            type_encoded = 0
        
        X_pred = pd.DataFrame([[type_encoded]], columns=['Type_Encoded'])
        X_pred_scaled = self.scaler_regression.transform(X_pred)
        
        flowrate = float(self.model_flowrate.predict(X_pred_scaled)[0])
        pressure = float(self.model_pressure.predict(X_pred_scaled)[0])
        temperature = float(self.model_temperature.predict(X_pred_scaled)[0])
        
        return {
            'equipment_type': equipment_type,
            'predicted_flowrate': round(flowrate, 2),
            'predicted_pressure': round(pressure, 2),
            'predicted_temperature': round(temperature, 2)
        }
    
    def predict_type(self, flowrate, pressure, temperature):
        """
        Predict equipment type from parameters (classification)
        
        Args:
            flowrate: Flowrate value
            pressure: Pressure value
            temperature: Temperature value
            
        Returns:
            dict: Predicted equipment type with confidence
        """
        if not self.is_trained or self.classifier_model is None:
            raise ValueError("Classification model not trained yet")
        
        # Create feature array
        X_pred = np.array([[flowrate, pressure, temperature]])
        X_pred_scaled = self.scaler_classification.transform(X_pred)
        
        # Predict
        predicted_type_encoded = self.classifier_model.predict(X_pred_scaled)[0]
        predicted_type = self.label_encoder.inverse_transform([predicted_type_encoded])[0]
        
        # Get confidence scores
        probabilities = self.classifier_model.predict_proba(X_pred_scaled)[0]
        confidence = float(max(probabilities))
        
        return {
            'predicted_type': predicted_type,
            'confidence': round(confidence * 100, 2),
            'input_parameters': {
                'flowrate': flowrate,
                'pressure': pressure,
                'temperature': temperature
            }
        }
    
    def save_model(self, filepath):
        """Save all trained models to file"""
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        
        model_data = {
            'model_flowrate': self.model_flowrate,
            'model_pressure': self.model_pressure,
            'model_temperature': self.model_temperature,
            'classifier_model': self.classifier_model,
            'scaler_regression': self.scaler_regression,
            'scaler_classification': self.scaler_classification,
            'label_encoder': self.label_encoder,
            'feature_names': self.feature_names,
            'training_history': self.training_history,
            'is_trained': self.is_trained
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, filepath):
        """Load all trained models from file"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model_flowrate = model_data['model_flowrate']
        self.model_pressure = model_data['model_pressure']
        self.model_temperature = model_data['model_temperature']
        self.classifier_model = model_data.get('classifier_model')
        self.scaler_regression = model_data.get('scaler_regression', StandardScaler())
        self.scaler_classification = model_data.get('scaler_classification', StandardScaler())
        self.label_encoder = model_data['label_encoder']
        self.feature_names = model_data['feature_names']
        self.training_history = model_data.get('training_history', {})
        self.is_trained = model_data['is_trained']
    
    def get_feature_importance(self):
        """
        Get feature importance from trained models
        
        Returns:
            dict: Feature importance for each model
        """
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        
        importance_data = {}
        
        # Regression models
        if hasattr(self.model_flowrate, 'feature_importances_'):
            importance_data['flowrate'] = {
                'features': self.feature_names,
                'importance': self.model_flowrate.feature_importances_.tolist()
            }
        
        if hasattr(self.model_pressure, 'feature_importances_'):
            importance_data['pressure'] = {
                'features': self.feature_names,
                'importance': self.model_pressure.feature_importances_.tolist()
            }
        
        if hasattr(self.model_temperature, 'feature_importances_'):
            importance_data['temperature'] = {
                'features': self.feature_names,
                'importance': self.model_temperature.feature_importances_.tolist()
            }
        
        # Classification model
        if self.classifier_model and hasattr(self.classifier_model, 'feature_importances_'):
            importance_data['classification'] = {
                'features': ['Flowrate', 'Pressure', 'Temperature'],
                'importance': self.classifier_model.feature_importances_.tolist()
            }
        
        return importance_data
