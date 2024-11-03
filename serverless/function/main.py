import os
import functions_framework
from google.cloud import storage
import subprocess
import tempfile
import json
from cloud_init_gen import CloudInitGenerator
from secret_manager import SecretManager

def setup_terraform_environment(tmp_dir):
    """Download and setup Terraform files from GCS"""
    storage_client = storage.Client()
    bucket = storage_client.bucket(os.environ.get('TERRAFORM_BUCKET'))
    
    # Download Terraform files
    terraform_files = ['main.tf', 'variables.tf', 'terraform.tfvars']
    for file in terraform_files:
        blob = bucket.blob(f'terraform/{file}')
        local_path = os.path.join(tmp_dir, file)
        blob.download_to_filename(local_path)
    
    # Initialize Terraform
    subprocess.run(['terraform', 'init'], cwd=tmp_dir, check=True)

@functions_framework.http

def generate_tfvars(tmp_dir, cloud_init_config, instance_name, request_json=None):
    """Generate terraform.tfvars.json file with VM configuration"""
    # Get configuration from request or use defaults
    machine_type = request_json.get('machine_type', 'e2-medium')
    disk_size = request_json.get('disk_size', 100)

    tfvars_content = {
        'instance_name': instance_name,
        'cloud_init_config': cloud_init_config,
        'machine_type': machine_type,
        'zone': os.environ.get('ZONE'),
        'project_id': os.environ.get('PROJECT_ID'),
        'network': 'default',
        'disk_size': disk_size,
        'labels': {
            'role': 'managed',
            'environment': 'development',
            'created_by': 'cloud_function'  # Example additional label
        },
        'tags': [
            instance_name,
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
        
def get_environment_config(): ### TEMPORARY SOLUTION
    """Get environment variables from .env file"""
    secret_manager = SecretManager()
    return secret_manager.get_all_secrets()
def create_vm(request):
    try:
        # Parse request
        request_json = request.get_json(silent=True)
        if not request_json:
            return {'error': 'No JSON data received'}, 400

        # Load environment variables
        env_vars = get_environment_config()

        if not env_vars['SSH_PUBLIC_KEY']:
            return {'error': 'SSH_PUBLIC_KEY not found in environment'}, 500

        # Initialize cloud-init generator
        cloud_init_gen = CloudInitGenerator(env_vars['BUCKET_NAME'])
        
        # Generate cloud-init config
        cloud_init = cloud_init_gen.generate_yaml(env_vars['SSH_PUBLIC_KEY'])

        # Create temporary directory for Terraform files
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Setup Terraform environment
            setup_terraform_environment(tmp_dir)
            
            # Generate instance name
            instance_name = f"cynthus-compute-instance-{os.urandom(4).hex()}"
            
            # Generate tfvars
            generate_tfvars(tmp_dir, cloud_init, instance_name)
            
            # Run Terraform apply
            result = subprocess.run(
                ['terraform', 'apply', '-auto-approve'],
                cwd=tmp_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {
                    'error': 'Terraform apply failed',
                    'details': result.stderr
                }, 500
            
            return {
                'message': f'VM creation initiated: {instance_name}',
                'terraform_output': result.stdout
            }, 200
            
    except Exception as e:
        return {'error': str(e)}, 500
    
    