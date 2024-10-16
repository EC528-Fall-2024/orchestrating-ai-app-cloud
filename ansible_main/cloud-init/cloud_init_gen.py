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

    # cloud-init config file
    yaml_content = f"""#cloud-config
users:
  - name: user
    sudo: ALL=(ALL) NOPASSWD:ALL
    ssh_authorized_keys:
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


output_path = os.path.join(current_dir, 'cloud-init-config.yaml')
generate_cloud_init_yaml(requirements_path, output_path)