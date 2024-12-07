import json
import requests
from .firebase_auth import *
from .bucket_ops import *
from urllib.parse import urlparse

def download_dataset_ex(config):
    """
    Makes a POST request to the dataset downloader service with the provided configuration.
    
    Args:
        config (dict): Configuration containing dataset URL, bucket name, and credentials
        
    Returns:
        dict: Response from the API
    """
    # API endpoint
    url = "https://us-central1-cynthusgcp-438617.cloudfunctions.net/dataset-downloader"
    
    # Headers for the request
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        # Make the POST request
        response = requests.post(url, json=config, headers=headers)
        
        # Check for specific error status codes
        if response.status_code == 500:
            print("Server encountered an internal error. This might be due to:")
            print("- Invalid dataset URL")
            print("- Invalid credentials")
            print("- Server-side processing error")
            print(f"Server response: {response.text}")
            return None
            
        # Raise an exception for other bad status codes
        response.raise_for_status()
        
        # Return the JSON response
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Server response: {e.response.text}")
        return None


def load_data():

    data = input("Are you loading local (L) or external (E) data?: ")

    if(data == 'L'):
        internal_data()

    elif(data == 'E'):
        external_data()

    else:
        print("Command not recognized. Please try again")


def external_data():
    # Config set up

    fire_token, uid = check_authentication()

    bucket = "user-bucket-"+ uid.lower()

    link = input("URL to the dataset: ")

    parsed_url = urlparse(link)
        
    if 'kaggle.com' in parsed_url.netloc:
        platform = 'kaggle'
    elif 'huggingface.co' in parsed_url.netloc:
        platform = 'huggingface'
    else:
        raise ValueError("Unsupported dataset URL")
    
    if platform == 'kaggle':

        username = input('Kaggle username: ')
        key = input('Kaggle API Key: ')

        config = {
            "dataset_url": link,
            "bucket_name": bucket,
            "credentials": {
                "kaggle": {
                    "username": username,
                    "key": key
                }
            }
        }

    elif platform == 'huggingface':

        token = input('HuggingFace Token: ')

        config = {
            "dataset_url": link,
            "bucket_name": bucket,
            "credentials": {
                "huggingface": {
                    "token": token
                }
            }
        }
    
    # Make the request
    result = download_dataset_ex(config)
    
    if result:
        print("Response:", json.dumps(result, indent=2))
    else:
        print("Failed to get response from the API")


def internal_data():

    data_path = input("Directory containing the new data: ")

    if data_path:
        data_path = Path(data_path)
        if not data_path.is_dir():
            print(f"Error: '{data_path}' is not a valid directory")
            return
        try:
            do_bucket_operations(str(data_path))
        except Exception as e:
            print(f"Error uploading data directory: {e}")
            return


def internal_data():

    data_path = input("Directory containing the new data: ")

    if data_path:
        data_path = Path(data_path)
        if not data_path.is_dir():
            print(f"Error: '{data_path}' is not a valid directory")
            return
        try:
            do_bucket_operations(str(data_path))
        except Exception as e:
            print(f"Error uploading data directory: {e}")
            return