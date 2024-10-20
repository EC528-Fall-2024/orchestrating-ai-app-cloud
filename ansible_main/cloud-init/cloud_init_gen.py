import os

current_dir = os.path.dirname(os.path.abspath(__file__))
requirements_path = os.path.join(current_dir, 'requirements.txt')

# CHANGE THIS SSH KEY
ssh_key = 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFbUbFFMOV4SKX3B5Jo/1tWXa6kNhRdLoGpQtTB7/uuG suijs@bu.edu'

def generate_cloud_init_yaml(requirements_path, output_path):
    # Read the requirements.txt file
    with open(requirements_path, 'r') as req_file:
        requirements = [line.strip() for line in req_file if line.strip() and not line.startswith('#')]

    # Create the cloud-init YAML content
    yaml_content = f"""#cloud-config
users:
  - name: user
    sudo: ALL=(ALL) NOPASSWD:ALL
    ssh_authorized_keys:
      # CHANGE THIS SSH KEY
      - {ssh_key}

ssh_pwauth: false

package_update: true
package_upgrade: true

packages:
  - python3-pip
  - openssh-server
  - nmap
  - openssh-client
  - python3
  - python3-pip
  - ansible
  - git
  - curl
  - wget
  - vim

runcmd:
  - sudo pip3 install {' '.join(requirements)}
"""
    # Write the cloud-init YAML file
    with open(output_path, 'w') as config_file:
        config_file.write(yaml_content)

# Use an environment variable for the output path, with a default fallback
default_output_path = 'cloud-init-config.yaml'
output_path = os.environ.get('CLOUD_INIT_OUTPUT_PATH', default_output_path)

# Ensure the output directory exists
os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

generate_cloud_init_yaml(requirements_path, output_path)

print(f"Cloud-init config file is located at {output_path}")