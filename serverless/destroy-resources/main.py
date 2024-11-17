import os
import functions_framework
from google.cloud import storage
import subprocess
import tempfile
import json
from terraform_configs import MAIN_TF, VARIABLES_TF

def setup_terraform_environment(tmp_dir, user_id):
    """Create Terraform files in temporary directory"""
    print(f"Setting up Terraform environment for user {user_id}...")
    
    main_tf_path = os.path.join(tmp_dir, 'main.tf')
    variables_tf_path = os.path.join(tmp_dir, 'variables.tf')
    
    with open(main_tf_path, 'w') as f:
        f.write(MAIN_TF)
    
    with open(variables_tf_path, 'w') as f:
        f.write(VARIABLES_TF)
    
    terraform_path = '/usr/bin/terraform'
    if not os.path.exists(terraform_path):
        raise RuntimeError("Terraform executable not found")
    
    # Initialize Terraform with the specific state for this user
    subprocess.run([
        terraform_path, 'init',
        '-backend-config', f'prefix=terraform/state/{user_id}/terraform.tfstate'
    ], cwd=tmp_dir, check=True)
    
    return terraform_path

@functions_framework.http
def destroy_resources(request):
    """Destroy VM and bucket resources.
    
    The format of the request is:
    {
        "user_id": "1234567890"
    }
    
    Args:
        request (Request): HTTP request object.
    Returns:
        Tuple[Dict[str, str], int]: A tuple containing a dictionary with the response message and the HTTP status code.
    """
    try:
        required_env_vars = {
            'PROJECT_ID': os.environ.get('PROJECT_ID'),
            'ZONE': os.environ.get('ZONE')
        }
        
        missing_vars = [var for var, value in required_env_vars.items() if not value]
        if missing_vars:
            return {
                'error': f'Missing required environment variables: {", ".join(missing_vars)}'
            }, 500
            
        request_json = request.get_json(silent=True)
        if not request_json or 'user_id' not in request_json:
            return {'error': 'user_id is required'}, 400

        user_id = request_json['user_id']
        
        # Create temporary directory for Terraform files
        tmp_dir = tempfile.mkdtemp(prefix=f"tf-destroy-{user_id}-")
        try:
            # Set up Terraform environment
            terraform_path = setup_terraform_environment(tmp_dir, user_id)
            
            # Run terraform destroy
            result = subprocess.run(
                [terraform_path, 'destroy', '-auto-approve'],
                cwd=tmp_dir,
                capture_output=True,
                text=True,
                env={
                    **os.environ,
                    'TF_VAR_project_id': os.environ.get('PROJECT_ID'),
                    'TF_VAR_zone': os.environ.get('ZONE'),
                    'TF_VAR_user_id': user_id
                }
            )
            
            if result.returncode != 0:
                return {
                    'error': 'Terraform destroy failed',
                    'details': result.stderr
                }, 500

            # Delete the associated buckets
            storage_client = storage.Client()
            buckets_to_delete = [
                f"user-bucket-{user_id}",
                f"output-user-bucket-{user_id}"
            ]

            for bucket_name in buckets_to_delete:
                try:
                    bucket = storage_client.get_bucket(bucket_name)
                    bucket.delete(force=True)
                except Exception as e:
                    print(f"Error deleting bucket {bucket_name}: {e}")

            return {
                'message': f'Resources destroyed for user {user_id}',
                'terraform_output': result.stdout
            }, 200

        finally:
            if os.path.exists(tmp_dir):
                import shutil
                shutil.rmtree(tmp_dir)

    except Exception as e:
        return {'error': str(e)}, 500