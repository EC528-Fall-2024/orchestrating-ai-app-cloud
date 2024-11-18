from google.cloud import storage
import os
import functions_framework
from urllib.parse import urlparse
import json
from pathlib import Path
from typing import Tuple, Dict, Any
from datasets import load_dataset
import pandas as pd

class DatasetDownloader:
    def __init__(self, credentials: Dict[str, Any]):
        self.credentials = credentials

    def download(self, platform: str, dataset_name: str, destination_path: str) -> None:
        """Downloads dataset based on platform."""
        if platform == 'kaggle':
            self._download_kaggle(dataset_name, destination_path)
        elif platform == 'huggingface':
            self._download_huggingface(dataset_name, destination_path)
        else:
            raise ValueError(f"Unsupported platform: {platform}")

    def _download_kaggle(self, dataset_name: str, destination_path: str) -> None:
        """Placeholder for Kaggle download functionality."""
        raise NotImplementedError("Kaggle download functionality is not implemented yet")

    def _download_huggingface(self, dataset_name: str, destination_path: str) -> None:
        """Download dataset from Hugging Face using datasets library."""
        if 'huggingface' not in self.credentials or not self.credentials['huggingface'].get('token'):
            raise ValueError("Missing Hugging Face token")

        try:
            token = self.credentials['huggingface']['token']
            # Load the dataset
            dataset = load_dataset(dataset_name, token=token)
            
            # Ensure the destination path exists
            os.makedirs(destination_path, exist_ok=True)
            
            # Save each split as a CSV file
            for split_name, split_data in dataset.items():
                # Convert to pandas DataFrame
                df = pd.DataFrame(split_data)
                
                # Save to CSV
                output_file = os.path.join(destination_path, f'{split_name}.csv')
                df.to_csv(output_file, index=False)
                
        except Exception as e:
            raise Exception(f"Hugging Face download failed: {str(e)}")

class URLParser:
    @staticmethod
    def parse_url(url: str) -> Tuple[str, str]:
        """Parse dataset information from URL."""
        parsed_url = urlparse(url)
        
        if 'kaggle.com' in parsed_url.netloc:
            platform = 'kaggle'
            path_parts = parsed_url.path.replace('/datasets/', '').strip('/').split('/')
        elif 'huggingface.co' in parsed_url.netloc:
            platform = 'huggingface'
            path_parts = parsed_url.path.replace('/datasets/', '').strip('/').split('/')
        else:
            raise ValueError("Unsupported dataset URL")
        
        if len(path_parts) < 2:
            raise ValueError(f"Invalid dataset URL format: {url}")
            
        dataset_name = '/'.join(path_parts)
        return platform, dataset_name

class GCSUploader:
    def __init__(self, bucket_name: str):
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(bucket_name)

    def upload_directory(self, source_dir: str, _: str) -> list:
        """Upload directory contents to GCS bucket root."""
        uploaded_files = []
        for root, _, files in os.walk(source_dir):
            for file in files:
                local_path = os.path.join(root, file)
                # Use just the filename for the blob path (root directory)
                blob = self.bucket.blob(file)
                blob.upload_from_filename(local_path)
                uploaded_files.append(file)
        return uploaded_files

@functions_framework.http
def download_dataset(request):
    """HTTP Cloud Function."""
    request_json = request.get_json(silent=True)
    
    if not request_json:
        return {'status': 'error', 'message': 'No JSON data received'}, 400
    
    dataset_url = request_json.get('dataset_url')
    bucket_name = request_json.get('bucket_name')
    credentials = request_json.get('credentials')
    
    if not all([dataset_url, bucket_name, credentials]):
        return {'status': 'error', 'message': 'Missing required parameters'}, 400
    
    temp_dir = Path('/tmp/dataset')
    
    try:
        # Parse URL
        parser = URLParser()
        platform, dataset_name = parser.parse_url(dataset_url)
        
        # Create temp directory
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Download dataset
        downloader = DatasetDownloader(credentials)
        try:
            downloader.download(platform, dataset_name, str(temp_dir))
        except NotImplementedError:
            return {
                'status': 'error',
                'message': 'Kaggle functionality is not implemented yet. Please use Hugging Face datasets.'
            }, 400
        
        # Upload to GCS
        uploader = GCSUploader(bucket_name)
        uploaded_files = uploader.upload_directory(str(temp_dir), dataset_name)
        
        return {
            'status': 'success',
            'message': f'Successfully downloaded {dataset_name} and uploaded files to root of bucket {bucket_name}',
            'platform': platform,
            'files': uploaded_files
        }, 200
        
    except ValueError as ve:
        return {'status': 'error', 'message': str(ve)}, 400
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500
    finally:
        # Cleanup
        if temp_dir.exists():
            for item in temp_dir.rglob('*'):
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    item.rmdir()
            temp_dir.rmdir()