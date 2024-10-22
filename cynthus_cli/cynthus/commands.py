import argparse
from pathlib import Path
import requests
import subprocess
import os
# import kaggle
from datasets import load_dataset_builder


def ping_intel():

    try:
        # Make a GET request to the API endpoint using requests.get()
        r = requests.get(
            'https://compute-us-region-2-api.cloud.intel.com/openapiv2/#/v1/ping')

        # Check if the request was successful (status code 200)
        if r.status_code == 200:
            print('Received response')
            return None
        else:
            print('Error:', r.status_code)
            return None

    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None


def setup_kaggle():
    """
    Provides instructions to the user on how to generate and set up the Kaggle API key.
    """
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


def download_kaggle_dataset(dataset, dest_path):
    """
    Download Kaggle dataset and print metadata like size.
    Args:
        dataset (str): The Kaggle dataset to download (e.g., 'username/dataset-name')
        dest_path (str): The local directory where the dataset will be downloaded
    """
    # Ensure the destination path exists
    os.makedirs(dest_path, exist_ok=True)

    try:
        # Check if Kaggle API key is set
        if not os.path.exists(os.path.expanduser("~/.kaggle/kaggle.json")):
            print("Kaggle API key is not set. Please set it up.")
            return

        # Download dataset
        kaggle.api.dataset_download_files(dataset, path=dest_path, unzip=True)

        # Calculate dataset size
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(dest_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)

        total_size_mb = total_size / (1024 * 1024)
        print(f"Dataset '{dataset}' downloaded to '{dest_path}'")
        print(f"Total size: {total_size_mb:.2f} MB")

    except Exception as e:
        print(f"Error downloading dataset: {e}")


def model_upload():
    print('Provide the link to the model you wish to upload: ')


def give_info():
    print('The VM package info can be found below: ')

# Initializes the project with the following directory strcuture
# project |
#         - src
#         - data
#         - config


def init_project(project_name):
    current_path = Path.cwd()
    new_directory_path = current_path / project_name

    try:
        new_directory_path.mkdir(parents=True, exist_ok=True)
        (new_directory_path / 'config').mkdir(parents=True, exist_ok=True)
        (new_directory_path / 'data').mkdir(parents=True, exist_ok=True)
        (new_directory_path / 'src').mkdir(parents=True, exist_ok=True)
    except Exception as error:
        print(f"Error creating project: {error}")

# Containerize the project within the directory and build its image
# creating a Dockerfile if one does not exist already, the Dockerfile
# is currenlty very hardcoded and will need to either be made dynamic
# or handled elsewhere (Ansible) later


def containerize_project(project_path):
    project_path = Path(project_path)

    if not project_path.is_dir():
        print(f"Error: '{project_path}' is not a valid directory")
        return

    dockerfile_path = project_path / 'Dockerfile'
    if not dockerfile_path.exists():
        with open(dockerfile_path, 'w') as f:
            f.write(f"FROM python:3.9\n")
            f.write(f"WORKDIR /src\n")
            f.write(f"COPY src/ .\n")

            # Removed the following because we might want to do installation through
            # Ansible and because I don't know how to dynamically locate the main
            # Python file from the user yet

            # f.write(f"RUN pip install -r requirements.txt\n")
            # f.write(f"CMD ['python', 'NAME_OF_CODE.py']")

    try:
        image_name = project_path.name
        print(f"building Docker image '{image_name}'...")
        subprocess.run(['docker', 'build', '-t', image_name,
                       str(project_path)], check=True)
        print(f"image '{image_name}' built successfully")
        project_push(image_name)

    except subprocess.CalledProcessError as error:
        print(f"Error: {error}")


# UNIMPLEMENTED
# Pushes the specified image to the specified container registry
# currently deadlocked by our inability to access Intel API and SSH implementation


def project_push(image_name):
    if (os.name == 'nt'):
        subprocess.run(["Get-Content", "creds\cynthusgcp-registry.json", "|", "docker",
                       "login", "-u", "_json_key", "--password-stdin", "https://us-east4-docker.pkg.dev"])
    else:
        subprocess.run(["cat", "creds\cynthusgcp-registry.json", "|", "docker", "login",
                       "-u", "_json_key", "--password-stdin", "https://us-east4-docker.pkg.dev"])
    subprocess.run(["docker", "tag", str(
        image_name), f"us-east4-docker.pkg.dev/cynthusgcp-438617/cynthus-images/{image_name}"])

    subprocess.run(
        ["docker", "push", f"us-east4-docker.pkg.dev/cynthusgcp-438617/cynthus-images/{image_name}"])


# UNIMPLEMENTED
# Auth the user into a specified cloud service using the supported login method, supported
# platforms include: ()


def project_auth(ssh_key, service):
    pass


# UNIMPLEMENTED
# Pulls data from a public data store and into a specified target cloud container
# For now, returns dataset size to test API calls


def project_datapull(url, target):
    if "huggingface.co" in url:
        hf_key = url.split("datasets/", 1)
        builder = load_dataset_builder(hf_key)
        print("Found dataset of size " + builder.info.download_size)
        '''
        import s3fs
        storage_options = {}
        fs = s3fs.S3FileSystem(**storage_options)
        builder.download_and_prepare(output_dir, storage_options=storage_options, file_format="parquet")
        '''


def cli_entry_point():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    parser_request = subparsers.add_parser('ping', help='Ping intel site')

    parser_print = subparsers.add_parser('print', help='Print help message')

    parser_info = subparsers.add_parser('info', help='Get VM package info')

    parser_init = subparsers.add_parser('init', help='Create Cynthus project')
    parser_init.add_argument(
        'project_name',
        help='The name of the project to create'
    )

    parser_containerize = subparsers.add_parser(
        'containerize', help='Containerize a project directory')
    parser_containerize.add_argument(
        'project_path',
        help='The path to the project directory to containerize'
    )

    parser_push = subparsers.add_parser(
        'push', help='Push a specified image to a specified cloud registry')
    parser_push.add_argument(
        'image_path',
        help='The image to containerize'
    )
    parser_push.add_argument(
        'registry',
        help='The name of the registry'
    )

    parser_auth = subparsers.add_parser(
        'ssh', help='Authenticate into a specified cloud registry')
    parser_auth.add_argument(
        'ssh_key',
        help='The public key of the user'
    )
    parser_auth.add_argument(
        'service',
        help='The cloud service to authenticate into'
    )

    parser_datapull = subparsers.add_parser(
        'datapull', help='Pull data from a target supported url into a VM')
    parser_datapull.add_argument(
        'url',
        help='The url to be pulled from, supports HuggingFace and Kaggle'
    )
    parser_datapull.add_argument(
        'target',
        help='The target to send the data'
    )

    parser_download_kaggle = subparsers.add_parser(
        'download-kaggle', help='Download dataset from Kaggle'
    )
    parser_download_kaggle.add_argument(
        'dataset', help='The Kaggle dataset to download (e.g., username/dataset-name)'
    )
    parser_download_kaggle.add_argument(
        'dest_path', help='The local directory where the dataset will be downloaded'
    )

    args = parser.parse_args()

    if args.command == 'ping':
        ping_intel()
    elif args.command == 'upload':
        model_upload()
    elif args.command == 'startVM':
        startVM()
    elif args.command == 'info':
        give_info()
    elif args.command == 'init':
        init_project(args.project_name)
    elif args.command == 'containerize':
        containerize_project(args.project_path)
    elif args.command == 'push':
        project_push(args.image_path, args.registry)
    elif args.command == 'ssh':
        project_ssh(args.ssh_key, args.service)
    elif args.command == 'datapull':
        project_datapull(args.url, args.target)
    elif args.command == 'setup_kaggle':
        setup_kaggle()
    elif args.command == 'download-kaggle':
        download_kaggle_dataset(args.dataset, args.dest_path)
    else:
        parser.print_help()
