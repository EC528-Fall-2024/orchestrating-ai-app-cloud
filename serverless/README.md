# VM Creation Cloud Function

## Overview
This is a serverless application that automatically creates and configures Virtual Machines (VMs) on Google Cloud Platform (GCP). Think of it as a robot that sets up computers in the cloud for you with just one click!

## What Does It Do?
1. Creates a new VM instance on Google Cloud
2. Sets up the VM with:
   - Python and essential development tools
   - Custom security settings
   - Required Python packages
   - SSH access for secure login
   - Firewall rules for network access

## How It Works
The application uses several key components:

### 1. Cloud Function (Main Entry Point)
The main function `create_vm` handles the entire process. It:
- Receives a request with VM specifications
- Generates necessary configuration files
- Uses Terraform to create the VM
- Returns the VM's IP address when done

### 2. Cloud Init Generator
Prepares the VM's initial setup script that:
- Creates a user named "cynthus"
- Installs necessary packages
- Sets up Python virtual environment
- Configures SSH access

### 3. Secret Manager
Safely manages sensitive information like:
- SSH keys
- Project credentials
- GCP configuration

## Requirements
- Google Cloud Platform account
- The following Python packages:
- python
    - google-cloud-storage
    - python-dotenv
    - functions-framework
    - pyyaml
    - google-cloud-functions
  

  
## How to Use

### 1. Deploy the Function
Deploy this code as a Cloud Function on Google Cloud Platform.

### 2. Make a Request
Send a POST request to the function URL with this JSON structure:

Example request:
```json
{
  "machine_type": "e2-medium",
  "disk_size": 100
}
```

### 3. Get Results
The function will return:
- Success message with VM name
- IP address of the new VM
- Terraform execution logs

## Security Features
- Automatic firewall configuration
- SSH key-based authentication (no passwords)
- Limited sudo access
- Secure package installation

## Common Use Cases
- Setting up development environments
- Creating testing servers
- Deploying application servers
- Setting up data science workstations

## Error Handling
The application includes comprehensive error handling for:
- Missing configuration
- Failed VM creation
- Network issues
- Invalid parameters

## Tips for New Users
1. Start with small machine types (e2-medium is good for testing)
2. Keep track of your VMs to avoid unnecessary costs
3. Always use the provided firewall rules
4. Make sure your SSH key is properly configured

## Need Help?
The code includes detailed comments and error messages to help you troubleshoot. Key files to look at:
- `main.py` - Main function logic
- `cloud_init_gen.py` - VM configuration
- `terraform_configs.py` - Infrastructure setup

Remember: Always review the costs associated with creating VMs on Google Cloud Platform!