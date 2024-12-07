import requests
from .firebase_auth import check_authentication

FUNCTION_URL = 'https://destroy-resources-531274461726.us-central1.run.app'


def destroy_resources():
    """Send request to Cloud Run to destroy resources."""
    token, _ = check_authentication()
    try:

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }

        print('\n🚀 Sending destroy request...')
        
        response = requests.delete(FUNCTION_URL, headers=headers)
        response.raise_for_status()
        
        print('✅ Resources destroyed:', response.json())
        
    except requests.exceptions.RequestException as e:
        error_data = {
            "message": e.response.json() if e.response else str(e),
            "status": e.response.status_code if e.response else "Unknown",
            "statusText": e.response.reason if e.response else "Unknown",
            "details": e.response.json().get("details", "No additional details") if e.response else "None"
        }
        print(f"❌ Error: {error_data}")
    except Exception as e:
        print(f"💥 Fatal error: {str(e)}")

