import os
from google.cloud import storage


class CloudInitGenerator:
    def __init__(self, bucket_name):
        if not bucket_name:
            raise ValueError("Bucket name is required")
        self.bucket_name = bucket_name # target bucket
        self.storage_client = storage.Client()
        try:
            self.bucket = self.storage_client.bucket(self.bucket_name)
            if not self.bucket.exists():
                raise ValueError(f"Bucket {bucket_name} does not exist")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize storage bucket: {e}")

    def load_requirements(self, requirements_blob_name='requirements.txt'):
        """Load requirements from Cloud Storage"""
        try:
            blob = self.bucket.blob(requirements_blob_name)
            requirements_content = blob.download_as_text()
            return [line.strip() for line in requirements_content.splitlines() 
                   if line.strip() and not line.startswith('#')]
        except Exception as e:
            print(f"Warning: Could not load requirements from GCS: {e}")
            # Fallback to basic requirements
            return [
                'ansible',
                'requests',
                # Add other default requirements
            ]
    def generate_cloud_init_yaml(self, ssh_key):
        """Generate the cloud-init YAML file"""
        requirements = self.load_requirements()

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

packages:
- python3-pip
- python3-dev
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
- build-essential
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

        print(f"Generated cloud-init YAML file")
        return yaml_content