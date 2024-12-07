import requests
from .firebase_auth import check_authentication

def update_src():
    """Incremental updates to src"""
    token, _ = check_authentication()
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        code_url = 'https://code-update-531274461726.us-east4.run.app'
        code_response = requests.post(code_url, headers=headers)
        code_response.raise_for_status()
        print('Code update successful:', code_response.json())

    except requests.exceptions.RequestException as e:
        print('Error:', {
            'message': e.response.json() if hasattr(e, 'response') else str(e),
            'status': e.response.status_code if hasattr(e, 'response') else None
        })
        raise


def update_data():
    """Incremental updates to src"""
    token, _ = check_authentication()
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        data_url = 'https://data-update-531274461726.us-east4.run.app'
        data_response = requests.post(data_url, headers=headers)
        data_response.raise_for_status()
        print('Data update successful:', data_response.json())
    except requests.exceptions.RequestException as e:
        print('Error:', {
            'message': e.response.json() if hasattr(e, 'response') else str(e),
            'status': e.response.status_code if hasattr(e, 'response') else None
        })
        raise
