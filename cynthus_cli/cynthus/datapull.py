import json
import requests
from .firebase_auth import *
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
        
        # Raise an exception for bad status codes
        response.raise_for_status()
        
        # Return the JSON response
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None


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



