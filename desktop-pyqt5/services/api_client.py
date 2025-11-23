"""
API Client for communicating with Django backend
"""
import requests
import json


class APIClient:
    """Client for making API requests to Django backend"""
    
    def __init__(self, base_url="http://localhost:8000/api"):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
    
    def set_token(self, token):
        """Set authentication token"""
        self.token = token
        self.session.headers.update({
            'Authorization': f'Token {token}'
        })
    
    def clear_token(self):
        """Clear authentication token"""
        self.token = None
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
    
    # Authentication endpoints
    def login(self, username, password):
        """
        Login user
        Returns: dict with token and user info
        """
        url = f"{self.base_url}/login/"
        data = {
            'username': username,
            'password': password
        }
        response = self.session.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        
        if 'token' in result:
            self.set_token(result['token'])
        
        return result
    
    def register(self, username, password, email=''):
        """
        Register new user
        Returns: dict with token and user info
        """
        url = f"{self.base_url}/register/"
        data = {
            'username': username,
            'password': password,
            'email': email
        }
        response = self.session.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        
        if 'token' in result:
            self.set_token(result['token'])
        
        return result
    
    def logout(self):
        """Logout user"""
        url = f"{self.base_url}/logout/"
        try:
            self.session.post(url)
        except:
            pass
        finally:
            self.clear_token()
    
    def get_user_info(self):
        """Get current user information"""
        url = f"{self.base_url}/user/"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    # Dataset endpoints
    def upload_csv(self, file_path):
        """
        Upload CSV file
        Args:
            file_path: Path to CSV file
        Returns: dict with processing summary
        """
        url = f"{self.base_url}/upload-csv/"
        
        with open(file_path, 'rb') as file:
            files = {'file': file}
            # Don't include content-type in headers, let requests handle it
            headers = {}
            if self.token:
                headers['Authorization'] = f'Token {self.token}'
            
            response = requests.post(url, files=files, headers=headers)
            response.raise_for_status()
            return response.json()
    
    def get_history(self):
        """
        Get upload history (last 5)
        Returns: list of dataset dictionaries
        """
        url = f"{self.base_url}/history/"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_dataset_detail(self, dataset_id):
        """
        Get detailed information about a dataset
        Args:
            dataset_id: ID of the dataset
        Returns: dict with dataset details
        """
        url = f"{self.base_url}/dataset/{dataset_id}/"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def generate_report(self, dataset_id=None):
        """
        Generate and download PDF report
        Args:
            dataset_id: Optional dataset ID (uses latest if not provided)
        Returns: PDF file content as bytes
        """
        url = f"{self.base_url}/generate-report/"
        if dataset_id:
            url += f"?dataset_id={dataset_id}"
        
        response = self.session.get(url)
        response.raise_for_status()
        return response.content
