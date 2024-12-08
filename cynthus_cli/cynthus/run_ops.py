import requests
from .firebase_auth import check_authentication

CLOUD_RUN_FUNCTION_URL = "https://us-east4-cynthusgcp-438617.cloudfunctions.net/run-container"

def run_container():
    """
    Sends a request to the Cloud Run function with the Firebase token for authentication.
    """
    token, _ = check_authentication()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(CLOUD_RUN_FUNCTION_URL, headers=headers)

        response.raise_for_status()
        print("Request succeeded...")
        print("VM running!")
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
