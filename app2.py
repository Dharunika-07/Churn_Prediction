'''from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
import pandas as pd
import os
import requests
import io
from urllib.parse import urljoin
import hashlib
import joblib

app = Flask(__name__)

# Configuration
GITHUB_REPO = "https://raw.githubusercontent.com/Dharunika-07/Churn_Prediction/main/"
MODEL_FILES = {
    'svm': {'filename': 'svm.pkl', 'expected_md5': None},
    'scaler': {'filename': 'scaler.pkl', 'expected_md5': None},
    'lda': {'filename': 'lda.pkl', 'expected_md5': None},
    #'pca': {'filename': 'pca1.pkl', 'expected_md5': None},
    'xgb': {'filename': 'xgb_model.pkl', 'expected_md5': None}
}

# Load dataset
try:
    df = pd.read_excel('customer_churn.xlsx')
    # Convert CustomerID to string and clean it
    df['CustomerID'] = df['CustomerID'].astype(str).str.strip()
    print("Dataset loaded successfully with shape:", df.shape)
    print("Sample CustomerIDs:", df['CustomerID'].head().tolist())
except Exception as e:
    print(f"Error loading dataset: {str(e)}")
    df = None

class ModelLoader:
    def __init__(self):
        self.models = {}
        self.loaded = False
    
    def download_model(self, model_name):
        """Download model from GitHub with verification"""
        url = urljoin(GITHUB_REPO, MODEL_FILES[model_name]['filename'])
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            if response.text.startswith('<!DOCTYPE html>'):
                raise ValueError(f"Received HTML instead of pickle file for {model_name}")
                
            content = response.content
            print(f"Downloaded {model_name} ({len(content)} bytes)")
            
            try:
                with io.BytesIO(content) as test_f:
                    pickle.load(test_f)
            except Exception as e:
                raise ValueError(f"Invalid pickle content for {model_name}: {str(e)}")
            
            return io.BytesIO(content)
        except Exception as e:
            raise Exception(f"Failed to download {model_name}: {str(e)}")
    
    def load_all_models(self):
        """Load all required models with error handling"""
        try:
            print("Loading models from GitHub...")
            
            models_to_load = ['scaler', 'lda', 'svm', 'xgb']
            
            for model_name in models_to_load:
                try:
                    with self.download_model(model_name) as f:
                        self.models[model_name] = pickle.load(f)
                    print(f"Successfully loaded {model_name}")
                except Exception as e:
                    print(f"ERROR loading {model_name}: {str(e)}")
                    raise
                    
            self.loaded = True
            pca_model = joblib.load('pca1.pkl')
            print("All models loaded successfully!")
        except Exception as e:
            print(f"Critical error loading models: {str(e)}")
            self.loaded = False
            raise

# Initialize model loader
model_loader = ModelLoader()

try:
    model_loader.load_all_models()
except Exception as e:
    print(f"Application startup failed: {str(e)}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/customer/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Endpoint to get customer details"""
    if df is None:
        return jsonify({
            'error': 'Dataset not loaded',
            'status': 'error'
        }), 503
    
    try:
        # Find customer in dataset (case insensitive)
        customer_data = df[df['CustomerID'].str.strip().str.lower() == customer_id.strip().lower()]
        
        if customer_data.empty:
            return jsonify({
                'error': f'Customer not found: {customer_id}',
                'status': 'error'
            }), 404
        
        # Convert to dictionary and handle NaN values
        customer_dict = customer_data.iloc[0].replace({np.nan: None}).to_dict()
        
        return jsonify({
            'status': 'success',
            'customer': customer_dict
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """Endpoint for making predictions"""
    if not model_loader.loaded:
        return jsonify({
            'error': 'Models not loaded',
            'status': 'error'
        }), 503
    
    if df is None:
        return jsonify({
            'error': 'Dataset not loaded',
            'status': 'error'
        }), 503
    
    try:
        # Get JSON data from request
        data = request.get_json()
        customer_id = data.get('CustomerID')
        
        if not customer_id:
            return jsonify({
                'error': 'CustomerID not provided',
                'status': 'error'
            }), 400
        
        # Find customer in dataset
        customer_data = df[df['CustomerID'].str.strip().str.lower() == customer_id.strip().lower()]
        
        if customer_data.empty:
            return jsonify({
                'error': f'Customer not found: {customer_id}',
                'status': 'error'
            }), 404
        
        # Prepare features
        input_data = customer_data.copy()
        
        # Churn Prediction
        churn_features = input_data.drop(columns=['Churn Label'], errors='ignore').fillna(0)
        scaled_data = model_loader.models['scaler'].transform(churn_features)
        lda_transformed = model_loader.models['lda'].transform(scaled_data)
        churn_prediction = model_loader.models['svm'].predict(lda_transformed)
        
        # CLTV Prediction
        cltv_features = input_data[[
            'Zip Code', 'Latitude', 'Longitude', 'Gender', 'Tenure Months',
            'Multiple Lines', 'Payment Method', 'Monthly Charges',
            'Total Charges', 'Churn Score'
        ]].fillna(0)
        pca_transformed = model_loader.models['pca'].transform(cltv_features)
        cltv_prediction = model_loader.models['xgb'].predict(pca_transformed)
        
        # Generate recommendations
        recommendations = []
        if churn_prediction[0] == 1:  # If churn predicted
            if 'Contract' in customer_data and customer_data['Contract'].values[0] == 'Month-to-month':
                recommendations.append("Offer annual contract discount (15% off)")
            if 'Monthly Charges' in customer_data and customer_data['Monthly Charges'].values[0] > 100:
                recommendations.append("Consider loyalty discount (10% off for 12 months)")
            if 'Tenure Months' in customer_data and customer_data['Tenure Months'].values[0] > 24:
                recommendations.append("Offer VIP customer benefits")
        
        return jsonify({
            'status': 'success',
            'churn_prediction': int(churn_prediction[0]),
            'churn_probability': 0.85,  # Replace with actual probability if available
            'cltv_prediction': float(cltv_prediction[0]),
            'customer_value': 'Premium' if cltv_prediction[0] > 5000 else 'Standard',
            'recommendations': recommendations
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)'''

from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
import pandas as pd
import os
import requests
import io
from urllib.parse import urljoin
import hashlib
import joblib

app = Flask(__name__)

# Configuration
GITHUB_REPO = "https://raw.githubusercontent.com/Dharunika-07/Churn_Prediction/main/"
MODEL_FILES = {
    'svm': {'filename': 'svm.pkl', 'expected_md5': None},
    'scaler': {'filename': 'scaler.pkl', 'expected_md5': None},
    'lda': {'filename': 'lda.pkl', 'expected_md5': None},
    'xgb': {'filename': 'xgb_model.pkl', 'expected_md5': None}
}

# Load dataset
try:
    df = pd.read_excel('customer_churn.xlsx')
    # Convert CustomerID to string and clean it
    df['CustomerID'] = df['CustomerID'].astype(str).str.strip()
    print("Dataset loaded successfully with shape:", df.shape)
    print("Sample CustomerIDs:", df['CustomerID'].head().tolist())
except Exception as e:
    print(f"Error loading dataset: {str(e)}")
    df = None

class ModelLoader:
    def __init__(self):
        self.models = {}
        self.loaded = False
    
    def download_model(self, model_name):
        """Download model from GitHub with verification"""
        url = urljoin(GITHUB_REPO, MODEL_FILES[model_name]['filename'])
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            if response.text.startswith('<!DOCTYPE html>'):
                raise ValueError(f"Received HTML instead of pickle file for {model_name}")
                
            content = response.content
            print(f"Downloaded {model_name} ({len(content)} bytes)")
            
            try:
                with io.BytesIO(content) as test_f:
                    pickle.load(test_f)
            except Exception as e:
                raise ValueError(f"Invalid pickle content for {model_name}: {str(e)}")
            
            return io.BytesIO(content)
        except Exception as e:
            raise Exception(f"Failed to download {model_name}: {str(e)}")
    
    def load_all_models(self):
        """Load all required models with error handling"""
        try:
            print("Loading models from GitHub...")
            
            models_to_load = ['scaler', 'lda', 'svm', 'xgb']
            
            for model_name in models_to_load:
                try:
                    with self.download_model(model_name) as f:
                        self.models[model_name] = pickle.load(f)
                    print(f"Successfully loaded {model_name}")
                except Exception as e:
                    print(f"ERROR loading {model_name}: {str(e)}")
                    raise
                    
            # Load PCA model from local file
            try:
                self.models['pca'] = joblib.load('pca1.pkl')
                print("PCA model loaded successfully")
            except Exception as e:
                raise Exception(f"Failed to load PCA model: {str(e)}")
                
            self.loaded = True
            print("All models loaded successfully!")
        except Exception as e:
            print(f"Critical error loading models: {str(e)}")
            self.loaded = False
            raise

# Initialize model loader
model_loader = ModelLoader()

try:
    model_loader.load_all_models()
except Exception as e:
    print(f"Application startup failed: {str(e)}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/customer/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Endpoint to get customer details"""
    if df is None:
        return jsonify({
            'error': 'Dataset not loaded',
            'status': 'error'
        }), 503
    
    try:
        # Find customer in dataset (case insensitive)
        customer_data = df[df['CustomerID'].str.strip().str.lower() == customer_id.strip().lower()]
        
        if customer_data.empty:
            return jsonify({
                'error': f'Customer not found: {customer_id}',
                'status': 'error'
            }), 404
        
        # Convert to dictionary and handle NaN values
        customer_dict = customer_data.iloc[0].replace({np.nan: None}).to_dict()
        
        return jsonify({
            'status': 'success',
            'customer': customer_dict
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """Endpoint for making predictions"""
    if not model_loader.loaded:
        return jsonify({
            'error': 'Models not loaded',
            'status': 'error'
        }), 503
    
    if df is None:
        return jsonify({
            'error': 'Dataset not loaded',
            'status': 'error'
        }), 503
    
    try:
        # Get JSON data from request
        data = request.get_json()
        customer_id = data.get('CustomerID')
        
        if not customer_id:
            return jsonify({
                'error': 'CustomerID not provided',
                'status': 'error'
            }), 400
        
        # Find customer in dataset
        customer_data = df[df['CustomerID'].str.strip().str.lower() == customer_id.strip().lower()]
        
        if customer_data.empty:
            return jsonify({
                'error': f'Customer not found: {customer_id}',
                'status': 'error'
            }), 404
        
        # Prepare features
        input_data = customer_data.copy()
        
        # Churn Prediction
        churn_features = input_data.drop(columns=['Churn Label'], errors='ignore').fillna(0)
        scaled_data = model_loader.models['scaler'].transform(churn_features)
        lda_transformed = model_loader.models['lda'].transform(scaled_data)
        churn_prediction = model_loader.models['svm'].predict(lda_transformed)
        
        # CLTV Prediction
        cltv_features = input_data[[
            'Zip Code', 'Latitude', 'Longitude', 'Gender', 'Tenure Months',
            'Multiple Lines', 'Payment Method', 'Monthly Charges',
            'Total Charges', 'Churn Score'
        ]].fillna(0)
        
        # Ensure features are in correct format for PCA
        cltv_features = cltv_features.values if hasattr(cltv_features, 'values') else cltv_features
        pca_transformed = model_loader.models['pca'].transform(cltv_features)
        cltv_prediction = model_loader.models['xgb'].predict(pca_transformed)
        
        # Generate recommendations
        recommendations = []
        if churn_prediction[0] == 1:  # If churn predicted
            if 'Contract' in customer_data and customer_data['Contract'].values[0] == 'Month-to-month':
                recommendations.append("Offer annual contract discount (15% off)")
            if 'Monthly Charges' in customer_data and customer_data['Monthly Charges'].values[0] > 100:
                recommendations.append("Consider loyalty discount (10% off for 12 months)")
            if 'Tenure Months' in customer_data and customer_data['Tenure Months'].values[0] > 24:
                recommendations.append("Offer VIP customer benefits")
        
        return jsonify({
            'status': 'success',
            'churn_prediction': int(churn_prediction[0]),
            'churn_probability': 0.85,  # Replace with actual probability if available
            'cltv_prediction': float(cltv_prediction[0]),
            'customer_value': 'Premium' if cltv_prediction[0] > 5000 else 'Standard',
            'recommendations': recommendations
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)