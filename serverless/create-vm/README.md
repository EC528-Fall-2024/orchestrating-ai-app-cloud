# Cloud-init-gen.py

This script generates a cloud-init YAML file for a VM instance. 
## Playbook triggering from cloud-init file in cloud-init-gen.py
### Requirements:
- activate service account has Cloud Run Invoker role
- jq package installed
### Steps:
- retrieve private IP of the control instance by sending a POST request to the get-private-ip cloud function
- retrieve the instance's private IP by sending a GET request to the metadata server
- send a POST request to the control instance with the instance's private IP in the JSON payload
- API deployed on the control instance should handle the request by dynamically generating the inventory file using the received private IP and running a playbook against that inventory file

