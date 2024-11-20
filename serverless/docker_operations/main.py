from google.auth.transport import requests
from google.auth import default
from google.oauth2 import service_account
import functions_framework
from firebase_admin import initialize_app, auth
import os

initialize_app()


def generate_artifact_registry_token():
    """Generate a short-lived access token for Artifact Registry."""
    # Get the default credentials and the required scopes
    credentials, project = default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"])

    # Generate the short-lived token for Artifact Registry
    auth_request = requests.Request()
    credentials.refresh(auth_request)
    return credentials.token


def verify_firebase_token(request):
    """Verify Firebase token from the request."""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None, ('Unauthorized', 401)
    id_token = auth_header.split('Bearer ')[1]

    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token['uid'], None
    except Exception as e:
        return None, ({'error': str(e)}, 401)


@functions_framework.http
def generate_upload_token(request):
    """Generate a temporary token for uploading Docker images to Artifact Registry."""
    if request.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }
        return ("", 204, headers)

    user_id, error = verify_firebase_token(request)
    if error:
        return error

    try:
        token = generate_artifact_registry_token()
        return {
            "message": "Token generated successfully.",
            "upload_token": token,
        }, 200
    except Exception as e:
        return {"error": f"Failed to generate token: {str(e)}"}, 500
