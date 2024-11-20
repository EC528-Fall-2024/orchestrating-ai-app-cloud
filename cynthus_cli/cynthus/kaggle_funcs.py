
#########################################################################################

# This section includes functions that interface with Kaggle. The functions include:
# - setup_kaggle()
# - download_kaggle_dataset(dataset, dest_path)

#########################################################################################


import os
#from kaggle.api.kaggle_api_extended import KaggleApi
from google.cloud import storage
import tempfile
import zipfile

# import kaggle

# Provides instructions to the user on how to generate and set up the Kaggle API key.

def setup_kaggle():

    print("To set up your Kaggle API key, follow these steps:")
    print("0.5 If you already have an Kaggle API key, use setup_kaggle_api")
    print("1. Go to your Kaggle account settings page: https://www.kaggle.com/account")
    print("2. Scroll down to the 'API' section.")
    print("3. Click on 'Create New API Token'. This will download a file named 'kaggle.json'.")
    print("4. Move this file to the directory ~/.kaggle/. If the directory does not exist, create it.")
    print("   You can use the following command:")
    print("   mkdir -p ~/.kaggle && mv /path/to/your/downloaded/kaggle.json ~/.kaggle/")
    print("5. Set the permissions of the kaggle.json file to read and write only for the user:")
    print("   chmod 600 ~/.kaggle/kaggle.json")
    print("You are now set up to use the Kaggle API!")


# Downloads a Kaggle dataset locally and print metadata like size.
# Inputs:
# - dataset (str): The Kaggle dataset to download (e.g., 'username/dataset-name')
# - dest_path (str): The local directory where the dataset will be downloaded
# CURRENTLY LOOKING TO PUSH KAGGLE DATASETS DIRECTLY TO S3 BUCKETS, SO FUNCTION MAY BE ADJUSTED/REMOVED

def download_kaggle_dataset(dataset, dest_path):
    
    # Ensure the destination path exists
    # os.makedirs(dest_path, exist_ok=True)

    # try:
    #     # Check if Kaggle API key is set
    #     if not os.path.exists(os.path.expanduser("~/.kaggle/kaggle.json")):
    #         print("Kaggle API key is not set. Please set it up.")
    #         return

    #     # Download dataset
    #     kaggle.api.dataset_download_files(dataset, path=dest_path, unzip=True)

    #     # Calculate dataset size
    #     total_size = 0
    #     for dirpath, dirnames, filenames in os.walk(dest_path):
    #         for f in filenames:
    #             fp = os.path.join(dirpath, f)
    #             total_size += os.path.getsize(fp)

    #     total_size_mb = total_size / (1024 * 1024)
    #     print(f"Dataset '{dataset}' downloaded to '{dest_path}'")
    #     print(f"Total size: {total_size_mb:.2f} MB")

    # except Exception as e:
    #     print(f"Error downloading dataset: {e}")

    print("Function triggered successfully")
    

def download_kaggle_to_gcs(
    dataset_name: str,
    bucket_name: str,
    gcs_prefix: str = "",
    project_id: str = None
):
    """
    Downloads a Kaggle dataset directly to Google Cloud Storage. Require kaggle api
    
    Args:
        dataset_name (str): Kaggle dataset name in format 'owner/dataset-name'
        bucket_name (str): GCS bucket name
        gcs_prefix (str): Optional prefix/folder in GCS bucket
        project_id (str): Optional Google Cloud project ID
    """
    # Initialize Kaggle API
    # Note: Requires ~/.kaggle/kaggle.json credentials file
    api = KaggleApi()
    api.authenticate()
    
    # Initialize GCS client
    # Note: Requires Google Cloud credentials
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    
    # Create a temporary directory to store downloaded dataset
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Downloading dataset: {dataset_name}")
        
        # Download dataset to temporary directory
        api.dataset_download_files(
            dataset_name,
            path=temp_dir,
            unzip=False
        )
        
        # Process the downloaded zip file
        zip_file_path = os.path.join(temp_dir, dataset_name.split('/')[-1] + '.zip')
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            for file_name in zip_ref.namelist():
                print(f"Processing file: {file_name}")
                
                # Read file content from the zip archive
                with zip_ref.open(file_name) as file_in_zip:
                    # Construct GCS path
                    gcs_path = os.path.join(gcs_prefix, file_name).lstrip('/')
                    
                    # Upload to GCS
                    blob = bucket.blob(gcs_path)
                    blob.upload_from_file(
                        file_in_zip,
                        content_type='application/octet-stream'
                    )
                    print(f"Uploaded to gs://{bucket_name}/{gcs_path}")

# Example usage
if __name__ == "__main__":
    # Example configuration
    DATASET_NAME = "steve1215rogg/student-lifestyle-dataset"  # Replace with your dataset
    BUCKET_NAME = "test-kaggle-bucket"             # Replace with your bucket
    GCS_PREFIX = "kaggle-datasets/lifestyle"       # Optional prefix
    PROJECT_ID = "your-project-id"                 # Your GCP project ID
    
    download_kaggle_to_gcs(
        dataset_name=DATASET_NAME,
        bucket_name=BUCKET_NAME,
        gcs_prefix=GCS_PREFIX,
        project_id=PROJECT_ID
    )
