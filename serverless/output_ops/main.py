from google.auth.transport import requests
from google.auth import default
from google.cloud import storage
from firebase_admin import initialize_app, auth
import functions_framework
import datetime
import tempfile
import os

initialize_app()


def verify_firebase_token(request):
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None, ('Unauthorized', 401)
    id_token = auth_header.split('Bearer ')[1]

    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token['uid'], None
    except Exception as e:
        return None, ({'error': str(e)}, 401)


def generate_signed_url(bucket_name, blob_name):
    """Generate a signed URL for a file in Cloud Storage."""
    credentials, _ = default()
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # Generate a signed URL valid for 15 minutes
    url = blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(minutes=15),
        method="GET",
    )
    return url


def compress_workspace(bucket_name, folder_name, archive_name):
    """Compress the workspace folder in Cloud Storage into an archive."""
    credentials, _ = default()
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)

    # Create a temporary directory to download files
    with tempfile.TemporaryDirectory() as temp_dir:
        folder_path = os.path.join(temp_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        # Download all files in the folder
        blobs = bucket.list_blobs(prefix=f"{folder_name}/")
        for blob in blobs:
            file_path = os.path.join(temp_dir, blob.name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            blob.download_to_filename(file_path)

        # Create the archive
        archive_path = os.path.join(temp_dir, archive_name)
        os.system(f"tar -czf {archive_path} -C {temp_dir} {folder_name}")

        # Upload the archive back to Cloud Storage
        archive_blob = bucket.blob(archive_name)
        archive_blob.upload_from_filename(archive_path)
        return archive_name


@functions_framework.http
def generate_workspace_url(request):
    """Generate a signed URL for the compressed workspace folder."""
    if request.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }
        return ("", 204, headers)

    # Verify Firebase token
    user_id, error = verify_firebase_token(request)
    if error:
        return error

    try:
        data = request.get_json()
        bucket_name = data.get("bucket_name")
        folder_name = "workspace"  # Folder to compress
        # Name of the compressed archive
        archive_name = f"{folder_name}.tar.gz"

        if not bucket_name:
            return {"error": "Bucket name is required"}, 400

        # Compress the workspace folder and generate a signed URL
        archive_blob_name = compress_workspace(
            bucket_name, folder_name, archive_name)
        signed_url = generate_signed_url(bucket_name, archive_blob_name)

        return {
            "message": "Signed URL generated successfully.",
            "signed_url": signed_url,
        }, 200

    except Exception as e:
        return {"error": f"Failed to generate signed URL: {str(e)}"}, 500
