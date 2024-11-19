import os
import functions_framework
from google.cloud import storage
import subprocess
import tempfile
import json
from terraform_configs import MAIN_TF, VARIABLES_TF

@functions_framework.http
def destroy_resources(request):
    """HTTP Cloud Function to destroy terraform resources."""
    try:
        request_json = request.get_json()
        if not request_json or 'user_id' not in request_json:
            return {'error': 'user_id is required'}, 400

        user_id = request_json['user_id']
        instance_name = f"cynthus-compute-instance-{user_id}"

        # Create temporary directory for Terraform files
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Setup Terraform environment
            terraform_path = setup_terraform_environment(tmp_dir, user_id)
            
            # Generate tfvars
            generate_tfvars(tmp_dir, instance_name, request_json)
            
            # Get the workspace name from the state file in GCS
            workspace_name = get_workspace_name(user_id)
            
            if not workspace_name:
                return {'error': 'No workspace found for this user'}, 404
            
            # Select the workspace
            subprocess.run(
                [terraform_path, 'workspace', 'select', workspace_name],
                cwd=tmp_dir,
                capture_output=True,
                check=True
            )
            
            # Run terraform destroy
            destroy_process = subprocess.run(
                [terraform_path, 'destroy', '-auto-approve'],
                cwd=tmp_dir,
                capture_output=True,
                text=True
            )
            
            if destroy_process.returncode != 0:
                print(f"Terraform destroy failed: {destroy_process.stderr}")
                return {'error': 'Terraform destroy failed', 'details': destroy_process.stderr}, 500
            
            # Clean up the workspace
            subprocess.run(
                [terraform_path, 'workspace', 'delete', workspace_name],
                cwd=tmp_dir,
                capture_output=True
            )
            
            bucket_deleted = delete_user_bucket(user_id)
            terraform_state_deleted = delete_terraform_state(user_id)

            response = {
                'message': 'Resources destroyed successfully',
                'workspace': workspace_name,
                'bucket_deleted': bucket_deleted,
                'terraform_state_deleted': terraform_state_deleted
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
    
    with open(main_tf_path, 'w') as f:
        f.write(MAIN_TF)
    
    with open(variables_tf_path, 'w') as f:
        f.write(VARIABLES_TF)
    
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
    
    # Initialize Terraform
    cloud_init_path = os.path.join(tmp_dir, 'cloud-init.yaml')
    with open(cloud_init_path, 'w') as f:
        f.write("""#cloud-config
runcmd:
  - echo "dummy config"
""")
        
    subprocess.run([
        terraform_path, 'init',
        '-backend-config', f'bucket=terraform-state-cynthus',
        '-backend-config', f'prefix=terraform/state/{user_id}'
    ], cwd=tmp_dir, check=True)
    
    return terraform_path

def generate_tfvars(tmp_dir, instance_name, request_json=None):
    """Generate terraform.tfvars.json file with VM configuration"""
    # Get configuration from request or use defaults
    machine_type = request_json.get('machine_type', 'e2-medium')
    disk_size = request_json.get('disk_size', 100)
    user_id = request_json.get('user_id', 'unknown')

    tfvars_content = {
        'instance_name': instance_name,
        'cloud_init_config': 'cloud-init.yaml',
        'machine_type': machine_type,
        'zone': os.environ.get('ZONE'),
        'project_id': os.environ.get('PROJECT_ID'),
        'network': 'default',
        'disk_size': disk_size,
        'user_id': user_id,
        'labels': {
            'role': 'managed',
            'environment': 'development',
            'user_id': user_id,
            'associated_bucket': f"user-bucket-{user_id}",
            'created_by': 'cloud_function'
        },
        'tags': [
            instance_name,
            f"user-{user_id}",
            'http-server',
            'https-server',
            'ssh-server'
        ],
        'firewall_ports': [
            '80', '443', '6379', '8001', '6006', '6007',
            '6000', '7000', '8808', '8000', '8888',
            '5173', '5174', '9009', '9000'
        ]
    }
    
    # Write the tfvars file
    tfvars_path = os.path.join(tmp_dir, 'terraform.tfvars.json')
    with open(tfvars_path, 'w') as f:
        json.dump(tfvars_content, f, indent=2)

def delete_user_bucket(user_id):
    """Delete the user's GCS bucket"""
    try:
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
    
def delete_terraform_state(user_id):
    """Delete the user's Terraform state files"""
    try:
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
