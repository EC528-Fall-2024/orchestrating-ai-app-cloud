import requests
import os
import tarfile
from pathlib import Path
from .firebase_auth import *

# Replace with your Cloud Run URL
API_URL = "https://us-central1-cynthusgcp-438617.cloudfunctions.net/output-ops/generate_workspace_url"


def get_signed_url(bucket_name, firebase_token):
    """Request a signed URL for the compressed workspace folder."""
    headers = {"Authorization": f"Bearer {firebase_token}"}
    response = requests.post(API_URL, headers=headers, json={
                             "bucket_name": bucket_name})
    response.raise_for_status()
    return response.json()["signed_url"]


def download_and_extract(signed_url, output_dir):
    """Download and extract the compressed workspace folder."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    archive_path = output_path / "workspace.tar.gz"

    # Download the archive
    print("Downloading workspace archive...")
    response = requests.get(signed_url)
    response.raise_for_status()
    with open(archive_path, "wb") as f:
        f.write(response.content)

    # Extract the archive
    print("Extracting workspace archive...")
    with tarfile.open(archive_path, "r:gz") as tar:
        tar.extractall(path=output_path)

    print(f"Workspace extracted to {output_path}")
    os.remove(archive_path)  # Clean up the archive file


def pull_output():
    output_dir = input("The directory to save the results to: ")
    try:
        # Authenticate and get the UID
        token, uid = check_authentication()
        if not token or not uid:
            raise ValueError(
                "Authentication failed. Cannot retrieve bucket information.")

        bucket_name = f"output-user-bucket-{uid}"

        signed_url = get_signed_url(bucket_name, token)
        download_and_extract(signed_url, output_dir)

        print(f"Workspace downloaded and extracted to {output_dir}")
    except Exception as e:
        print(f"Error: {e}")


# pull_output()
 