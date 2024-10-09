def generate_cloud_init_yaml(requirements_path, output_path):
    # Read the requirements.txt file
    with open(requirements_path, 'r') as req_file:
        requirements = req_file.read()

    # Create the cloud-init YAML content
    yaml_content = f"""#cloud-config

package_update: true
package_upgrade: true

packages:
  - python3-pip

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