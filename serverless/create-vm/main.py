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
    print("Starting Terraform environment setup...")
    
    # Debug: Check PATH
    print(f"Current PATH: {os.environ.get('PATH')}")
    
    # Debug: Check if terraform is executable
    os.system("which terraform")
    os.system("ls -la /usr/bin/terraform")
    
    print(f"Temporary directory path: {tmp_dir}")
    print(f"Contents of tmp_dir before creating files: {os.listdir(tmp_dir)}")
    
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
    subprocess.run([terraform_path, 'init'], cwd=tmp_dir, check=True)
    return terraform_path

def generate_tfvars(tmp_dir, cloud_init_config, instance_name, request_json=None):
    """Generate terraform.tfvars.json file with VM configuration"""
    # Get configuration from request or use defaults
    machine_type = request_json.get('machine_type', 'e2-medium')
    disk_size = request_json.get('disk_size', 100)
    user_id = request_json.get('user_id', 'unknown')

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
            'user_id': user_id,
            'associated_bucket': f"user-bucket-{user_id}",
            'created_by': 'cloud_function'  # Example additional label
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



@functions_framework.http      
def get_environment_config(): ### TEMPORARY SOLUTION
    """Get environment variables from .env file"""
    secret_manager = SecretManager()
    return secret_manager.get_all_secrets()

def create_vm(request):
    try:
        request_json = request.get_json(silent=True)
        print(f"Received request JSON: {request_json}")
        if not request_json:
            return {'error': 'No JSON data received'}, 400

        env_vars = get_environment_config()
        with open('key.json', 'r') as f:
           key_json_content = f.read()
        
        print(f"Key JSON content: {key_json_content}")
        
        cloud_init_gen = CloudInitGenerator(f"user-bucket-{request_json['user_id']}")
        cloud_init_yaml = cloud_init_gen.generate_cloud_init_yaml(env_vars['SSH_PUBLIC_KEY'], key_json_content)
        
        tmp_dir = tempfile.mkdtemp(prefix=f"tf-{request_json['user_id']}-")
        try:
            cloud_init_path = os.path.join(tmp_dir, 'cloud-init-config.yaml')
            with open(cloud_init_path, 'w') as f:
                f.write(cloud_init_yaml)
            
            terraform_path = setup_terraform_environment(tmp_dir)
            instance_name = f"cynthus-compute-instance-{request_json['user_id']}"
            
            generate_tfvars(tmp_dir, cloud_init_path, instance_name, request_json)
            
            # Create unique workspace
            workspace_name = f"{instance_name}-{os.urandom(4).hex()}"
            subprocess.run(
                [terraform_path, 'workspace', 'new', workspace_name],
                cwd=tmp_dir,
                capture_output=True,
                check=True
            )
            
            # Select the workspace
            subprocess.run(
                [terraform_path, 'workspace', 'select', workspace_name],
                cwd=tmp_dir,
                capture_output=True,
                check=True
            )
            
            # Then proceed with your existing terraform apply
            result = subprocess.run(
                [terraform_path, 'apply', '-auto-approve'],
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

        finally:
            # Clean up the temporary directory
            if os.path.exists(tmp_dir):
                import shutil
                shutil.rmtree(tmp_dir)

    except Exception as e:
        return {'error': str(e)}, 500