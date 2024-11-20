from google.cloud import storage
import functions_framework
from firebase_admin import initialize_app, auth
import json
import os
import subprocess

initialize_app()

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
def bucket_operations(request):
    """Main function to handle all bucket operations"""
    # Enable CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        return ('', 204, headers)

    # Verify token
    user_id, error = verify_firebase_token(request)
    user_id = user_id.lower()
    if error:
        return error

    storage_client = storage.Client()
    bucket_name = f"user-bucket-{user_id}"
    bucket_output_name = f"output-user-bucket-{user_id}"

    try:
        # Parse request data
        data = request.get_json() if request.is_json else {}
        operation = data.get('operation', '')

        if request.method == 'POST':
            if operation == 'create':
                return create_bucket(bucket_name, storage_client)
            
            elif operation == 'create_output':
                return create_output_bucket(bucket_output_name, storage_client)
            
            elif operation == 'upload':
                file_content = data.get('content')
                file_path = data.get('path')
                return upload_file(bucket_name, file_path, file_content, storage_client)
            
            elif operation == 'generate_requirements':  # Add this new condition
                return generate_requirements(bucket_name, storage_client)
            
            else:
                return {'error': 'Invalid operation'}, 400

        elif request.method == 'GET':
            operation = request.args.get('operation', '')
            
            if not operation:
                return ({'error': 'Operation is required'}, 400, headers)
            
            if operation == 'list':
                bucket = storage_client.bucket(bucket_name)
                if not bucket.exists():
                    return ({'error': f'Bucket {bucket_name} does not exist'}, 404, headers)
                result, status_code = list_files(bucket_name, storage_client)
                return (result, status_code, headers)
            
            elif operation == 'read':
                file_path = request.args.get('path')  # Get path from query parameters
                return read_file(bucket_name, file_path, storage_client)
            
            elif operation == 'download':
                file_path = request.args.get('path')  # Get path from query parameters
                return download_file(bucket_name, file_path, storage_client)
            
            elif operation == 'generate_requirements':
                return generate_requirements(bucket_name, storage_client)
            
            else:
                return {'error': 'Invalid operation'}, 400  

    except Exception as e:
        return ({
            'error': str(e),
            'details': {
                'type': type(e).__name__,
                'operation': request.args.get('operation') if request.method == 'GET' else None
            }
        }, 400, headers)
    
def generate_requirements(bucket_name, storage_client):
    """Generate requirements.txt using pipreqs for files in src folder"""
    try:
        # Create temporary directory
        temp_dir = '/tmp/src'
        os.makedirs(temp_dir, exist_ok=True)
        
        # Download all files from src/ in the bucket to temp directory
        bucket = storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix='src/')
        
        for blob in blobs:
            if blob.name == 'src/':  # Skip directory itself
                continue
            local_path = os.path.join('/tmp', blob.name)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            blob.download_to_filename(local_path)
        
        # Run pipreqs
        subprocess.run(['pipreqs', '--force', '--mode', 'no-pin', temp_dir], check=True)
        
        # Read and upload requirements.txt
        with open(os.path.join(temp_dir, 'requirements.txt'), 'r') as f:
            requirements_content = f.read()
        
        # Upload requirements.txt to src folder
        requirements_blob = bucket.blob('src/requirements.txt')
        requirements_blob.upload_from_string(requirements_content)
        
        return {
            'message': 'Requirements.txt generated and uploaded successfully to src folder',
            'content': requirements_content
        }, 200
        
    except subprocess.CalledProcessError as e:
        return {'error': f'Failed to run pipreqs: {str(e)}'}, 500
    except Exception as e:
        return {'error': f'Error generating requirements: {str(e)}'}, 500   
    
def create_bucket_class_location(bucket_name, storage_client):
    """Create a new bucket in the US region with the coldline storage class."""
    # Check if bucket already exists
    bucket = storage_client.bucket(bucket_name)
    if bucket.exists():
        return bucket

    # Set storage class and location, then create
    bucket.storage_class = "COLDLINE"
    try:
        new_bucket = storage_client.create_bucket(bucket, location="us")
        return new_bucket
    except Exception as e:
        raise Exception(f"Failed to create bucket: {str(e)}")
    
def create_bucket(bucket_name, storage_client):
    """Create a new bucket"""
    bucket = create_bucket_class_location(bucket_name, storage_client)
    return {
        'message': f'Bucket {bucket_name} created successfully',
        'bucket_name': bucket_name
    }, 200

def create_output_bucket(bucket_name, storage_client):
    """Create a new output bucket"""
    bucket = create_bucket_class_location(bucket_name, storage_client)
    return {
        'message': f'Bucket {bucket_name} created successfully',
        'bucket_name': bucket_name
    }, 200

def upload_file(bucket_name, file_path, file_content, storage_client):
    """Upload a file to the bucket"""
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    blob.upload_from_string(file_content)
    return {
        'message': f'File uploaded successfully to {file_path}',
        'path': file_path
    }, 200

# Function updated to show progress of file upload to user

# def upload_file_progress(bucket_name, file_path, file_content, storage_client):
#     """Upload a file to the bucket"""
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(file_path)
    
#     with open(file_path, 'rb') as f:
#         blob.upload_from_file(f, progress_bar=True)

#     return {
#         'message': f'File uploaded successfully to {file_path}',
#         'path': file_path
#     }, 200


def list_files(bucket_name, storage_client):
    """List all files in the bucket"""
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs()
    files = [blob.name for blob in blobs]
    return {
        'files': files
    }, 200

def read_file(bucket_name, file_path, storage_client):
    """Read a file from the bucket"""
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    content = blob.download_as_text()
    return {
        'content': content,
        'path': file_path
    }, 200

def download_file(bucket_name, file_path, storage_client):
    """Generate a signed URL for downloading the file"""
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    url = blob.generate_signed_url(
        version="v4",
        expiration=300,  # 5 minutes
        method="GET"
    )
    return {
        'download_url': url,
        'path': file_path
    }, 200