import requests
import json
import os
import base64
from google.auth import default
from google.auth.transport.requests import Request
def get_access_token():
    credentials, project = default()
    credentials.refresh(Request())
    return credentials.token, project

def create_instance(project_id, zone, instance_name, machine_type, cloud_init_file_path, tags):
    with open(cloud_init_file_path, 'r') as cloud_init_file:
        cloud_init_data = cloud_init_file.read()
    cloud_init_encoded = base64.b64encode(cloud_init_data.encode('utf-8')).decode('utf-8')
    instance_config = {
        "name": instance_name,
        "machineType": f"zones/{zone}/machineTypes/{machine_type}",
        "disks": [{
            "boot": True,
            "autoDelete": True,
            "initializeParams": {
                "sourceImage": "projects/ubuntu-os-cloud/global/images/family/ubuntu-2204-lts"
            }
        }],
        "networkInterfaces": [{
            "network": "global/networks/default",
            "accessConfigs": [{
                "name": "External NAT",
                "type": "ONE_TO_ONE_NAT"
            }]
        }],
        "metadata": {
            "items": [{
                "key": "user-data",
                "value": cloud_init_encoded
            }]
        },
        "tags": {
            "items": tags
        }
    }

    # Define the API URL
    url = f"https://compute.googleapis.com/compute/v1/projects/{project_id}/zones/{zone}/instances"
    token,_ = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    #make the post request
    response = requests.post(url, headers=headers, json=instance_config)

    if response.status_code == 200 or response.status_code == 201:
        print(f"Instance {instance_name} creation initiated.")
    else:
        print(f"Failed to create instance {instance_name}.")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
def main():
    project_id = os.getenv("GCP_PROJECT_ID", "changeme")
    zone = os.getenv("GCP_ZONE", "xxxxxx")
    machine_type = "e2-micro"
    cloud_init_file_path = os.path.join(os.path.dirname(__file__), "target_cloudinit.yaml")

    # Create the instance
    create_instance(
        project_id=project_id,
        zone=zone,
        instance_name="managed-node-instance",
        machine_type=machine_type,
        cloud_init_file_path=cloud_init_file_path,
        tags=["managed"]
    )


if __name__ == "__main__":
    main()
