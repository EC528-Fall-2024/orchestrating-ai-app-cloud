import requests
from .firebase_auth import *
from pathlib import Path
import json

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

def do_bucket_operations(directory_path: str):
    try:
        token, _ = check_authentication()

        create_bucket(token, "create")
        create_bucket(token, "create_output")

        directory = Path(directory_path)
        if not directory.is_dir():
            raise ValueError(f"{directory_path} is not a valid directory")

        for file in directory.rglob('*'):
            if file.is_file():
                relative_path = file.relative_to(directory)
                upload_path = f"data/{relative_path}"
                upload_file(token, str(file), upload_path)

        report_file = Path(__file__).parent / "report-ip.sh"
        report_path = "src/report-ip.sh"
        upload_file(token, str(report_file), report_path)

        machine_type = input("Enter the machine type (e.g., n1-standard-1): ").strip()
        disk_size = input("Enter the disk size (e.g., 50 for 50GB): ").strip()

        config = {
            "machine_type": machine_type,
            "disk_size": disk_size
        }
        config_file = Path(__file__).parent / "config.json"
        with open(config_file, "w") as file:
            json.dump(config, file, indent=4)

        config_upload_path = "config.json"
        upload_file(token, str(config_file), config_upload_path)
        config_file.unlink()

        generate_requirements(token)

    except Exception as e:
        print("Error in do_bucket_operations:", e)
