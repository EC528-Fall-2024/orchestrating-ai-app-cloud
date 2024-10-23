import os


def load_env(env_path):
    env_vars = {}
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip().strip("'").strip('"')
    return env_vars


current_dir = os.path.dirname(os.path.abspath(__file__))
requirements_path = os.path.join(current_dir, 'requirements.txt')
env_path = os.path.join(current_dir, '.env')

# Load environment variables from .env file
env_vars = load_env(env_path)

# Use the SSH_PUBLIC_KEY from .env file
ssh_key = env_vars.get('SSH_PUBLIC_KEY')

if not ssh_key:
    raise ValueError("SSH_PUBLIC_KEY not found in .env file")


def generate_cloud_init_yaml(requirements_path, output_path):
    # Read the requirements.txt file
    with open(requirements_path, 'r') as req_file:
        requirements = [
            line.strip() for line in req_file if line.strip() and not line.startswith('#')]

    # Create the cloud-init YAML content
    yaml_content = f"""#cloud-config
users:
  - name: cynthus
    sudo: ALL=(ALL) NOPASSWD:ALL
    shell: /bin/bash
    groups: [admin, users, wheel]
    ssh_authorized_keys:
      - {ssh_key}

ssh_pwauth: false

package_update: true
package_upgrade: true


# Install basic packages
packages:
  - python3-pip
  - python3-dev  # Required for some pip packages
  - python3-venv
  - openssh-server
  - nmap
  - openssh-client
  - python3
  - ansible
  - git
  - curl
  - wget
  - vim
  - build-essential  # Required for some pip packages
  - software-properties-common
  - ca-certificates
  - apt-transport-https

runcmd:
  - until dpkg -l | grep -q python3; do sleep 5; done
  - until command -v python3 >/dev/null 2>&1; do sleep 5; done
  - mkdir -p /home/cynthus/venv
  - python3 -m venv /home/cynthus/venv
  - chown -R cynthus:cynthus /home/cynthus/venv
  - /home/cynthus/venv/bin/pip install --upgrade pip
  - /home/cynthus/venv/bin/pip install {' '.join(requirements)}
  - chown -R cynthus:cynthus /home/cynthus/venv 
  - echo "Python venv setup complete" > /home/cynthus/venv_setup_complete
  - chown cynthus:cynthus /home/cynthus/venv_setup_complete
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
