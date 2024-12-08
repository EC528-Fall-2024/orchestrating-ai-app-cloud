import os
import functions_framework
from firebase_admin import auth, initialize_app
import subprocess
import tempfile
import json
import requests

initialize_app()

function_url = "http://10.150.0.36:5000/run" # code-updateAPI ENDPOINT ON THE CONTROL NODE

def verify_firebase_token(request):
    """Helper function to verify Firebase token"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None, ('Unauthorized', 401)
    id_token = auth_header.split('Bearer ')[1]
    
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token['uid'], None
    except Exception as e:
        return None, ({'error': str(e)}, 401)
    
@functions_framework.http
def run_container(request):
    print("Run container function triggered")
    
    user_id, error = verify_firebase_token(request)
    
    if error:
        return error
    
    print(f"User ID: {user_id}")
    
    user_id = user_id.lower()
    
    request_data = {
        "user_id": user_id,
    }
    
    try:
        headers = {
            'Content-Type': 'application/json'
        }
        print(f"Sending request to {function_url} with data: {request_data}")
        response = requests.post(function_url, json=request_data, headers=headers)
        print(f"Response status: {response.status_code}")
        response.raise_for_status()
        return response.json(), 200
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {str(e)}")
        return {'error': str(e)}, 500
    
    print("Run container function completed")