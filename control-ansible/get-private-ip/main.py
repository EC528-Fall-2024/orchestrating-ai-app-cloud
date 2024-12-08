import os
import functions_framework
from googleapiclient.discovery import build


# Initialize the Compute Engine API client
def get_compute_client():
    """
    Authenticates and returns a Compute Engine client. Google Cloud function is deployed with a service account.
    """
    return build('compute', 'v1')


@functions_framework.http
def get_private_ip(request):
    # Read configuration from environment variables
    project_id = os.environ.get("GCP_PROJECT_ID", "your-project-id")
    zone = os.environ.get("CONTROL_INSTANCE_ZONE", "your-zone")
    instance_name = os.environ.get("CONTROL_INSTANCE_NAME", "control-ansible")

    # Log configuration for debugging
    print(f"Project: {project_id}, Zone: {zone}, Instance: {instance_name}")

    try:
        # Initialize the Compute Engine client
        compute = get_compute_client()

        # Fetch the instance details
        instance = compute.instances().get(
            project=project_id,
            zone=zone,
            instance=instance_name
        ).execute()

        # Extract the private IP address
        network_interfaces = instance.get("networkInterfaces", [])
        if not network_interfaces:
            return {"error": "No network interfaces found for the instance."}, 404

        private_ip = network_interfaces[0].get("networkIP", "Unknown")
        return {"instance_name": instance_name, "private_ip": private_ip}, 200

    except Exception as e:
        error_message = f"Failed to retrieve private IP: {e}"
        print(error_message)  # Log the error
        return {"error": error_message}, 500
