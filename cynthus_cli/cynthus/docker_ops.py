import subprocess
import requests
from firebase_auth import check_authentication

API_URL = "https://us-central1-cynthusgcp-438617.cloudfunctions.net/docker-operations/generate-upload-token"


def get_temp_token():
    token, _ = check_authentication()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(API_URL, headers=headers)
    response.raise_for_status()
    return response.json()["upload_token"]


def docker_push(image_name, upload_token):
    subprocess.run(["docker", "login", "-u", "oauth2accesstoken", "--password-stdin", "us-east4-docker.pkg.dev"],
                   input=upload_token, text=True, check=True)

    artifact_image_name = f"us-east4-docker.pkg.dev/cynthusgcp-438617/cynthus-images/{image_name}"
    subprocess.run(["docker", "tag", image_name,
                   artifact_image_name], check=True)

    subprocess.run(["docker", "push", artifact_image_name], check=True)
    print(f"Image pushed successfully to {artifact_image_name}")


if __name__ == "__main__":
    IMAGE_NAME = "src"
    try:
        upload_token = get_temp_token()
        docker_push(IMAGE_NAME, upload_token)
    except Exception as e:
        print(f"Error: {str(e)}")
