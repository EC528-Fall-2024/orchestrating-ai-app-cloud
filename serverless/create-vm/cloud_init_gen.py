import os
from google.cloud import storage
import time 
import json

class CloudInitGenerator:
    def __init__(self, bucket_name, max_retries=5, retry_delay=2):
        if not bucket_name:
            raise ValueError("Bucket name is required")
        self.bucket_name = bucket_name
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.storage_client = storage.Client()
        try:
            self.bucket = self.storage_client.bucket(self.bucket_name)
            if not self.bucket.exists():
                raise ValueError(f"Bucket {bucket_name} does not exist")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize storage bucket: {e}")

    def load_requirements(self, requirements_blob_name='src/requirements.txt'):
        """Load requirements from Cloud Storage with retry logic"""
        attempts = 0
        last_exception = None

        while attempts < self.max_retries:
            try:
                blob = self.bucket.blob(requirements_blob_name)
                if blob.exists():
                    requirements_content = blob.download_as_text()
                    return [line.strip() for line in requirements_content.splitlines() 
                           if line.strip() and not line.startswith('#')]
                else:
                    print(f"Attempt {attempts + 1}/{self.max_retries}: requirements.txt not found yet")
            except Exception as e:
                last_exception = e
                print(f"Attempt {attempts + 1}/{self.max_retries} failed: {e}")
            
            attempts += 1
            if attempts < self.max_retries:
                time.sleep(self.retry_delay * attempts)
        
        print(f"Warning: Could not load requirements from GCS after {self.max_retries} attempts: {last_exception}")
        return [
            'ansible',
            'requests',
        ]
        
    def generate_cloud_init_yaml(self, ssh_key, key_json_content):
        """Generate the cloud-init YAML file"""
        requirements = self.load_requirements()
        
        try:
            key_json_dict = json.loads(key_json_content)
            formatted_key_json = json.dumps(key_json_dict, indent=2)
            # Add proper YAML indentation (2 spaces for YAML standard)
            formatted_key_json = '\n'.join('        ' + line for line in formatted_key_json.splitlines())
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON content in key_json_content")

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

write_files:
  - path: /home/cynthus/key.json
    permissions: '0600'
    owner: root:root
    content: |
{formatted_key_json}

packages:
  - openssh-server
  - nmap
  - openssh-client
  - git
  - curl
  - wget
  - vim
  - build-essential
  - software-properties-common
  - ca-certificates
  - apt-transport-https
  - jq

runcmd:
  - mkdir -p /home/cynthus/.config/gcloud/logs
  - mkdir -p /home/cynthus/snap
  - chown -R cynthus:cynthus /home/cynthus/snap
  - chown -R cynthus:cynthus /home/cynthus/.config
  - chmod 700 /home/cynthus/.config/gcloud
  - sudo chmod a+rwx /home/cynthus/key.json
  - sudo su - cynthus -c "sudo gcloud auth activate-service-account --key-file=/home/cynthus/key.json"
  - mkdir -p /home/cynthus/workspace
  - sudo gsutil cp -r gs://{self.bucket_name}/data/* /home/cynthus/workspace
  - sudo chown -R cynthus:cynthus /home/cynthus/workspace
  - sudo -u cynthus gcloud auth activate-service-account --key-file=/home/cynthus/key.json
  - cd /home/cynthus/workspace && sudo chmod a+x report-ip.sh
  - cd /home/cynthus/workspace && ./report-ip.sh
"""

        print("YAML content generated")
        
        return yaml_content