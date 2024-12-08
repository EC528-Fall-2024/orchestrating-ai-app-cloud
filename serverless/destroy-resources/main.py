import os
import functions_framework
from google.cloud import storage
import subprocess
import tempfile
import json
from terraform_configs import MAIN_TF, VARIABLES_TF
from firebase_admin import auth, initialize_app

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
def destroy_resources(request):
    """HTTP Cloud Function to destroy terraform resources."""
    print("Destroying resources...")
    user_id, error = verify_firebase_token(request)
    if error:
        return error
       
    user_id = user_id.lower()
    
    request_json = request.get_json() if request.is_json else {}
    
    
    
    try:
        instance_name = f"cynthus-compute-instance-{user_id}"

        # Create temporary directory for Terraform files
        with tempfile.TemporaryDirectory() as tmp_dir:
            print(f"Created temporary directory: {tmp_dir}")
            
            # Setup Terraform environment
            terraform_path = setup_terraform_environment(tmp_dir, user_id)
            
            # Get the workspace name from the state file in GCS
            workspace_name = get_workspace_name(user_id)
            
            print(f"Workspace name: {workspace_name}")
            
            if not workspace_name:
                return {'error': 'No workspace found for this user'}, 404
            
            print(f"Getting terraform variables for user: {user_id}")
            
            storage_client = storage.Client()
            tfvars_bucket = storage_client.bucket('terraform-state-cynthus')
            tfvars_blob = tfvars_bucket.blob(f'terraform/vars/{user_id}/terraform.tfvars.json')

            if not tfvars_blob.exists():
                return {'error': 'No terraform variables found for this user'}, 404
       
            # Download and save tfvars file
            tfvars_path = os.path.join(tmp_dir, 'terraform.tfvars.json')
            with open(tfvars_path, 'wb') as tfvars_file:
                tfvars_blob.download_to_file(tfvars_file)
                # Make sure the file is written to disk
                tfvars_file.flush()
                
            print(f"Terraform variables file downloaded to: {tfvars_path}")
            
            cloud_init_path = os.path.join(tmp_dir, 'cloud-init-config.yaml')
            with open(cloud_init_path, 'w') as f:
                f.write("""#cloud-config
runcmd:
  - echo "Dummy file for terraform destroy"
""")
            # Add the cloud-init file to the Terraform configuration
            with open(tfvars_path, 'r') as f:
                tfvars_data = json.load(f)
           
            tfvars_data['cloud_init_config'] = cloud_init_path
           
            with open(tfvars_path, 'w') as f:
                json.dump(tfvars_data, f)
           
            print(f"Terraform variables file updated with cloud-init path: {tfvars_path}")
           
            subprocess.run(
                [
                    terraform_path, 'init',
                    '-backend-config=bucket=terraform-state-cynthus',
                    f'-backend-config=prefix=terraform/state/{user_id}',
                    '-input=false',  # Disable interactive prompts
                    '-no-color'      # Clean output for logs
                ],
                cwd=tmp_dir,
                capture_output=True,
                text=True,
                check=True
            )
               
            print(f"Initialized Terraform in directory: {tmp_dir}")

            # Select the workspace
            subprocess.run(
                [terraform_path, 'workspace', 'select', workspace_name],
                cwd=tmp_dir,
                capture_output=True,
                text=True,
                check=True
            )
            
            print(f"Selected workspace: {workspace_name}")
            
            # Run terraform destroy
            destroy_process = subprocess.run(
                [terraform_path, 'destroy', '-auto-approve'],
                cwd=tmp_dir,
                capture_output=True,
                text=True
            )
            
            if destroy_process.returncode != 0:
                error_message = f"Terraform destroy failed:\nSTDOUT:\n{destroy_process.stdout}\nSTDERR:\n{destroy_process.stderr}"
                print(error_message)  # This will go to Cloud Functions logs
                return {
                   'error': 'Terraform destroy failed',
                   'stdout': destroy_process.stdout,
                   'stderr': destroy_process.stderr
               }, 500
            
            # Clean up the workspace
            subprocess.run(
                [terraform_path, 'workspace', 'delete', workspace_name],
                cwd=tmp_dir,
                capture_output=True
            )
            
            bucket_deleted = delete_user_bucket(user_id)
            terraform_state_deleted = delete_terraform_state(user_id)
            output_bucket_deleted = delete_output_bucket(user_id)

            response = {
                'message': 'Resources destroyed successfully',
                'workspace': workspace_name,
                'bucket_deleted': bucket_deleted,
                'terraform_state_deleted': terraform_state_deleted,
                'output_bucket_deleted': output_bucket_deleted
            }
            
            return response
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return {'error': str(e)}, 500

def get_workspace_name(user_id):
    """Get the workspace name from GCS state files"""
    storage_client = storage.Client()
    bucket = storage_client.bucket('terraform-state-cynthus')
    prefix = f'terraform/state/{user_id}/'
    
    # List all objects in the user's state directory
    blobs = bucket.list_blobs(prefix=prefix)
    
    for blob in blobs:
        # Look for the workspace-specific state file
        if blob.name.endswith('.tfstate') and 'default.tfstate' not in blob.name:
            # Extract workspace name from the path
            workspace_name = blob.name.split('/')[-1].replace('.tfstate', '')
            return workspace_name
    
    return None

def setup_terraform_environment(tmp_dir, user_id):
    """Create Terraform files in temporary directory"""
    print("Starting Terraform environment setup...")
    
    main_tf_path = os.path.join(tmp_dir, 'main.tf')
    variables_tf_path = os.path.join(tmp_dir, 'variables.tf')
    
    try:
        with open(main_tf_path, 'w', encoding='utf-8') as f:
            f.write(MAIN_TF)
        
        with open(variables_tf_path, 'w', encoding='utf-8') as f:
            f.write(VARIABLES_TF)
    except Exception as e:
        print(f"Error writing Terraform files: {str(e)}")
        raise
    
    # Check multiple possible Terraform locations
    terraform_paths = [
        '/usr/bin/terraform',
        '/usr/local/bin/terraform',
        '/opt/terraform/terraform'
    ]
    
    terraform_path = None
    for path in terraform_paths:
        if os.path.exists(path):
            terraform_path = path
            break
    
    if not terraform_path:
        raise RuntimeError("Terraform executable not found in expected locations")
    
    print(f"Using Terraform at: {terraform_path}")
    
    return terraform_path

def delete_user_bucket(user_id):
    """Delete the user's GCS bucket"""
    try:
        print(f"Deleting bucket for user: {user_id}")
        
        storage_client = storage.Client()
        bucket_name = f"user-bucket-{user_id}"
        bucket = storage_client.bucket(bucket_name)
        
        # Delete all objects in the bucket first
        blobs = bucket.list_blobs()
        for blob in blobs:
            blob.delete()
            
        # Delete the bucket itself
        bucket.delete()
        return True
    except Exception as e:
        print(f"Error deleting bucket: {str(e)}")
        return False
    
def delete_output_bucket(user_id):
    """Delete the user's output GCS bucket"""
    try:
        print(f"Deleting output bucket for user: {user_id}")
        
        storage_client = storage.Client()
        bucket_name = f"output-user-bucket-{user_id}"
        bucket = storage_client.bucket(bucket_name)
        
        # Delete all objects in the bucket first
        blobs = bucket.list_blobs()
        for blob in blobs:
            blob.delete()
            
        # Delete the bucket itself
        bucket.delete()
        return True
    except Exception as e:
        print(f"Error deleting output bucket: {str(e)}")
        return False
    
def delete_terraform_state(user_id):
    """Delete the user's Terraform state files"""
    try:
        print(f"Deleting Terraform state for user: {user_id}")
        
        storage_client = storage.Client()
        bucket_name = f"terraform-state-cynthus"
        bucket = storage_client.bucket(bucket_name)
        
        prefix = f"terraform/state/{user_id}"
        
        blobs = bucket.list_blobs(prefix=prefix)
        for blob in blobs:
            blob.delete()
        return True
    except Exception as e:
        print(f"Error deleting Terraform state: {str(e)}")
        return False
