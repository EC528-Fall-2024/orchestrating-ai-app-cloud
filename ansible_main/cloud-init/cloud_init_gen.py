def generate_cloud_init_yaml(requirements_path, output_path):
    # Read the requirements.txt file
    with open(requirements_path, 'r') as req_file:
        requirements = req_file.read()

    # Create the cloud-init YAML content

    # cloud-init config file
    yaml_content = f"""#cloud-config
users:
  - name: user
    sudo: ALL=(ALL) NOPASSWD:ALL
    ssh_authorized_keys:
      - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFNeLRIWWuEqoZ8mHZb8Q6xSqTzb2aFymxuzXBN12Jzn suij2@DESTRUCTION-SUI # CHANGE THIS SSH KEY

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


write_files:
  - path: /requirements.txt
    content: |
{requirements.strip().replace('\n', '\n      ')}

runcmd:
  - pip3 install -r /requirements.txt
"""

    # Write the cloud-init YAML file
    with open(output_path, 'w') as config_file:
        config_file.write(yaml_content)

# Usage
requirements_path = 'requirements.txt'
output_path = 'cloud-init-config.yaml'
generate_cloud_init_yaml(requirements_path, output_path)