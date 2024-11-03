import os
import functions_framework
from google.cloud import storage
import subprocess
import tempfile
import json
from cloud_init_gen import CloudInitGenerator
from secret_manager import SecretManager
from terraform_configs import MAIN_TF, VARIABLES_TF

def setup_terraform_environment(tmp_dir):
    """Create Terraform files in temporary directory"""
    print(f"Temporary directory path: {tmp_dir}")
    print(f"Contents of tmp_dir before creating files: {os.listdir(tmp_dir)}")
    
    main_tf_path = os.path.join(tmp_dir, 'main.tf')
    variables_tf_path = os.path.join(tmp_dir, 'variables.tf')
    
    print(f"Writing main.tf to: {main_tf_path}")
    with open(main_tf_path, 'w') as f:
        f.write(MAIN_TF)
    
    print(f"Writing variables.tf to: {variables_tf_path}")
    with open(variables_tf_path, 'w') as f:
        f.write(VARIABLES_TF)
    
    print(f"Contents of tmp_dir after creating files: {os.listdir(tmp_dir)}")
    
    # Check if terraform executable exists in PATH
    result = subprocess.run(['which', 'terraform'], capture_output=True, text=True)
    print(f"Terraform executable location: {result.stdout if result.returncode == 0 else 'Not found'}")
    
    subprocess.run(['terraform', 'init'], cwd=tmp_dir, check=True)

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



@functions_framework.http      
def get_environment_config(): ### TEMPORARY SOLUTION
    """Get environment variables from .env file"""
    secret_manager = SecretManager()
    return secret_manager.get_all_secrets()

def create_vm(request):
    try:
        request_json = request.get_json(silent=True)
        if not request_json:
            return {'error': 'No JSON data received'}, 400

        env_vars = get_environment_config()
        
        # Initialize CloudInitGenerator with your GCS bucket name
        cloud_init_gen = CloudInitGenerator(env_vars['REQUIREMENTS_BUCKET'])
        
        # Generate cloud-init config using SSH key from env vars
        cloud_init_yaml = cloud_init_gen.generate_cloud_init_yaml(env_vars['SSH_PUBLIC_KEY'])
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Save cloud-init config to Terraform directory
            cloud_init_path = os.path.join(tmp_dir, 'cloud-init-config.yaml')
            with open(cloud_init_path, 'w') as f:
                f.write(cloud_init_yaml)
            
            setup_terraform_environment(tmp_dir)
            instance_name = f"cynthus-compute-instance-{os.urandom(4).hex()}"
            
            # Pass cloud_init_path to generate_tfvars
            generate_tfvars(tmp_dir, cloud_init_path, instance_name, request_json)
            
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