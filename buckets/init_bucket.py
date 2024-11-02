from google.cloud import storage
import uuid
# log into gcp: gcloud auth application-default login
#

def create_bucket_hierarchical_namespace(bucket_name):
    """Creates a bucket with hierarchical namespace enabled."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    bucket.iam_configuration.uniform_bucket_level_access_enabled = True
    bucket.hierarchical_namespace_enabled = True
    bucket.create()

    print(f"Created bucket {bucket_name} with hierarchical namespace enabled.")


def create_bucket_class_location(bucket_name):
    """Create a new bucket in the US region with the coldline storage class."""
    storage_client = storage.Client()

    # Check if bucket already exists
    bucket = storage_client.bucket(bucket_name)
    if bucket.exists():
        print(f"Bucket {bucket_name} already exists.")
        return bucket

    # Set storage class and location, then create
    bucket.storage_class = "COLDLINE"
    new_bucket = storage_client.create_bucket(bucket, location="us")

    print(
        f"Created bucket {new_bucket.name} in {new_bucket.location} with storage class {new_bucket.storage_class}"
    )
    return new_bucket



def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a local file to the bucket.
    upload_blob("your-bucket-name", "local/path/to/file.txt", "folder-in-bucket/file.txt")
    """
    # Initialize the storage client
    storage_client = storage.Client()
    
    # Get the bucket
    bucket = storage_client.bucket(bucket_name)
    
    # Create a blob (object in GCS)
    blob = bucket.blob(destination_blob_name)
    
    # Upload the file to the blob
    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket.
    e.g. download_blob("your-bucket-name", "folder-in-bucket/file.txt", "local/path/to/file.txt")
    """
    # Initialize the storage client
    storage_client = storage.Client()
    
    # Get the bucket
    bucket = storage_client.bucket(bucket_name)
    
    # Get the blob (file in GCS)
    blob = bucket.blob(source_blob_name)
    
    # Download the blob to a local file
    blob.download_to_filename(destination_file_name)

    print(f"Blob {source_blob_name} downloaded to {destination_file_name}.")


def read_blob(bucket_name, blob_name): 

    """Reads the contents of a blob in the bucket.
    content = read_blob("your-bucket-name", "folder-in-bucket/file.txt")
    """
    # Initialize the storage client
    storage_client = storage.Client()
    
    # Get the bucket
    bucket = storage_client.bucket(bucket_name)
    
    # Get the blob (file in GCS)
    blob = bucket.blob(blob_name)
    
    # Read the blob’s content as a string
    content = blob.download_as_text()

    print(f"Content of {blob_name}:")
    print(content)
    return content


def list_blobs(bucket_name): 
    """Lists all the blobs in the bucket.
    list_blobs("your-bucket-name")
    """
    # Initialize the storage client
    storage_client = storage.Client()
    
    # Get the bucket
    bucket = storage_client.bucket(bucket_name)
    
    # List all blobs in the bucket
    blobs = bucket.list_blobs()

    print("Files in the bucket:")
    for blob in blobs:
        print(blob.name)



if __name__ == "__main__":
    
    # Define the bucket name and file paths
    bucket_name = f"test-bucket-{uuid.uuid4()}"  # unique bucket name

    local_file_path = "test.txt"
    destination_blob_name = "uploaded-files/file.txt"
    download_file_path = "/Users/guzhaowen/Downloads/test.txt"

    create_bucket_class_location(bucket_name)


    # Upload the file
    upload_blob(bucket_name, local_file_path, destination_blob_name)

    # List files in the bucket
    list_blobs(bucket_name)

    # Read the uploaded file's content directly
    read_blob(bucket_name, destination_blob_name)

    # Download the file
    download_blob(bucket_name, destination_blob_name, download_file_path)