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

    def load_requirements(self, requirements_blob_name='src/requirements.txt'):
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
    def generate_cloud_init_yaml(self, ssh_key, key_json_content):
        """Generate the cloud-init YAML file"""
        requirements = self.load_requirements()
        
        formatted_key_json = '\n'.join('      ' + line for line in key_json_content.splitlines())
# make sure that the activate service account has Cloud Run Invoker role
# make sure jq package is installed 
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
- path: /home/cynthus/key.json  # Adjusted path to be in cynthus home directory
  permissions: '0600'
  owner: root:root        # Changed owner to match your user
  content: |
{formatted_key_json}

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
- jq

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
- sudo chmod a+rwx /home/cynthus/key.json
- sudo su - cynthus -c "sudo gcloud auth activate-service-account --key-file=/home/cynthus/key.json"
- mkdir -p /home/cynthus/workspace
- sudo gsutil cp -r gs://{self.bucket_name}/src/* /home/cynthus/workspace
- sudo chown -R cynthus:cynthus /home/cynthus/workspace
- cd /home/cynthus/workspace && for f in *.py; do if [ -f "$f" ]; then /home/cynthus/venv/bin/python "$f"; fi; done
- echo "Uploading workspace results to output bucket..."
- sudo gsutil cp -r /home/cynthus/workspace/* gs://output-{self.bucket_name}/workspace/
- echo "Workspace upload complete" > /home/cynthus/upload_complete
- CONTROL_PRIV_IP=$(curl -s -X POST -H "Authorization: Bearer $(gcloud auth print-identity-token)" https://get-private-ip-531274461726.us-central1.run.app | jq -r '.private_ip')
- PRIVATE_IP=$(curl -H "Metadata-Flavor: Google" http://169.254.169.254/computeMetadata/v1/instance/network-interfaces/0/ip)
- PAYLOAD='{"ip":"'$PRIVATE_IP'"}'
- curl -X POST "http://$CONTROL_PRIV_IP/run" -H "Content-Type: application/json" -d "$PAYLOAD"

"""

        print(f"Generated cloud-init YAML file")
        print(f"YAML content: {yaml_content}")
        
        return yaml_content