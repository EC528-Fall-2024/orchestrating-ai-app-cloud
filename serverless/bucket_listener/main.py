import functions_framework
from google.cloud import storage
import requests
import re
import json

@functions_framework.cloud_event
def handle_bucket_creation(cloud_event):
    # Extract bucket name from the event
    data = cloud_event.data
    print(f"Received event data: {data}")
    
    # Extract bucket name from the correct path
    bucket_name = data["resource"]["labels"]["bucket_name"]
    print(f"Extracted bucket name: {bucket_name}")
    
    if bucket_name.startswith('user-bucket-'):
    # Extract the ID from the bucket name using regex
        match = re.search(r'user-bucket-([a-zA-Z0-9]+)$', bucket_name)
        if not match:
            print(f"Bucket {bucket_name} doesn't match expected format")
            return
        
        user_id = match.group(1)
        
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        
        try:
            # Read config.json from the bucket
            config_blob = bucket.blob('config.json')
            config_content = config_blob.download_as_string()
            vm_config = json.loads(config_content)
            
            vm_request_data = {
                "machine_type": vm_config.get('machine_type'),
                "disk_size": vm_config.get('disk_size'),
                "user_id": user_id
            }
        except Exception as e:
            print(f"Error reading config.json: {e}")
            
            vm_request_data = {
                "machine_type": "e2-medium",
                "disk_size": 100,
                "user_id": user_id
            }
            
        # Replace with your VM creation function URL
        vm_function_url = "https://create-vm-531274461726.us-central1.run.app"
        
        response = requests.post(vm_function_url, json=vm_request_data)
        if response.status_code != 200:
            print(f"Failed to create VM: {response.text}")
            return
        
        print(f"Successfully initiated VM creation for bucket {bucket_name}")