import requests
from firebase_auth import check_authentication

FUNCTION_URL = 'https://us-central1-cynthusgcp-438617.cloudfunctions.net/bucket_operations'


def create_bucket(token: str, operation: str):
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = requests.post(
            FUNCTION_URL,
            headers=headers,
            json={"operation": operation},
        )
        response.raise_for_status()
        print(f"{operation.capitalize()} bucket operation completed:",
              response.json())
    except Exception as e:
        print("Error in create_bucket:", e)
        raise


def upload_file(token: str, file_path: str, upload_path: str):
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        with open(file_path, "r") as file:
            content = file.read()
        response = requests.post(
            FUNCTION_URL,
            headers=headers,
            json={"operation": "upload", "path": upload_path, "content": content},
        )
        response.raise_for_status()
        print("File uploaded successfully:", response.json())
    except Exception as e:
        print("Error in upload_file:", e)
        raise


def generate_requirements(token: str):
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = requests.post(
            FUNCTION_URL,
            headers=headers,
            json={"operation": "generate_requirements"},
        )
        response.raise_for_status()
        print("Requirements generated:", response.json())
    except Exception as e:
        print("Error in generate_requirements:", e)
        raise


def read_file(token: str, file_path: str):
    try:
        headers = {
            "Authorization": f"Bearer {token}",
        }
        response = requests.get(
            f"{FUNCTION_URL}?operation=read&path={file_path}", headers=headers
        )
        response.raise_for_status()
        print("File content:", response.json())
    except Exception as e:
        print("Error in read_file:", e)
        raise


def generate_download_url(token: str, file_path: str):
    try:
        headers = {
            "Authorization": f"Bearer {token}",
        }
        response = requests.get(
            f"{FUNCTION_URL}?operation=download&path={file_path}", headers=headers
        )
        response.raise_for_status()
        print("Download URL:", response.json())
    except Exception as e:
        print("Error in generate_download_url:", e)
        raise


def bucket_operations(src_file: str, config_file: str):
    try:
        token, _ = check_authentication()
        create_bucket(token, "create")
        create_bucket(token, "create_output")
        upload_file(token, src_file, f"src/{src_file}")
        upload_file(token, config_file, config_file)
        generate_requirements(token)
        # read_file(token, f"src/{src_file}")
        # generate_download_url(token, f"src/{src_file}")
    except Exception as e:
        print("Error in test_bucket_operations:", e)
