import os
from kaggle.api.kaggle_api_extended import KaggleApi
from google.cloud import storage
import tempfile
import zipfile

def download_kaggle_to_gcs(
    dataset_name: str,
    bucket_name: str,
    gcs_prefix: str = "",
    project_id: str = None
):
    """
    Downloads a Kaggle dataset directly to Google Cloud Storage.
    
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
