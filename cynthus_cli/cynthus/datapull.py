import json
import requests
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
    url = "https://dataset-downloader-531274461726.us-central1.run.app"
    
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
    link = input("URL to the dataset: ")

    parsed_url = urlparse(link)
        
    if 'kaggle.com' in parsed_url.netloc:
        platform = 'kaggle'
    elif 'huggingface.co' in parsed_url.netloc:
        platform = 'huggingface'
    else:
        raise ValueError("Unsupported dataset URL")
    
    if platform == 'kaggle':

        bucket = input('The name of the gcs bucket: ')
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

        bucket = input('The name of the gcs bucket: ')
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


# def create_json_template():
  
#     location = input("HuggingFace(H) or Kaggle(K): ")

#     if location == 'H':

#         template = {
#             "dataset_url": "",
#             "bucket_name": "your-gcs-bucket",
#             "credentials": {
#                 "huggingface": {
#                     "token": "your-huggingface-token"
#                 }
#             }
#         }

#         with open('configure_huggingface.json', 'w') as f:
#             json.dump(template, f, indent=4)

#         dataset = input('The URL of the dataset your pulling: ')
#         bucket = input('The name of the gcs bucket: ')
#         token = input('HuggingFace Token: ')

#         update_fields = {
#             "dataset_url" : dataset,
#             "bucket_name" : bucket
#         }

#         with open('configure_huggingface.json', 'r+') as f:
#             data = json.load(f)

#             for field, new_value in update_fields.items():
#                 data[field] = new_value

#             data['credentials']['huggingface']['token'] = token

#             f.seek(0)
#             json.dump(data, f, indent=4)
#             f.truncate()

#         print('File configure_huggingface.json created successfully!')
    
#     elif location == 'K':

#         template = {
#             "dataset_url": "",
#             "bucket_name": "your-gcs-bucket",
#             "credentials": {
#                 "kaggle": {
#                     "username": "your-kaggle-username",
#                     "key": "your-kaggle-api-key"
#                 }
#             }
#         }

#         with open('configure_kaggle.json', 'w') as f:
#             json.dump(template, f, indent=4)

#         dataset = input('The URL of the dataset your pulling: ')
#         bucket = input('The name of the gcs bucket: ')
#         username = input('Kaggle username: ')
#         key = input('Kaggle API Key: ')

#         update_fields = {
#             "dataset_url" : dataset,
#             "bucket_name" : bucket
#         }

#         with open('configure_kaggle.json', 'r+') as f:
#             data = json.load(f)

#             for field, new_value in update_fields.items():
#                 data[field] = new_value

#             data['credentials']['kaggle']['username'] = username
#             data['credentials']['kaggle']['key'] = key

#             f.seek(0)
#             json.dump(data, f, indent=4)
#             f.truncate()

#         print('File configure_kaggle.json successfully created!')
    
#     else:
#         print('Invalid command, please try again')
