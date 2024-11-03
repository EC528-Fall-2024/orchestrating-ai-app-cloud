
#########################################################################################

# This section includes functions that interface with Kaggle. The functions include:
# - setup_kaggle()
# - download_kaggle_dataset(dataset, dest_path)

#########################################################################################

import os
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