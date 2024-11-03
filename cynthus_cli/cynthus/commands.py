import argparse
from pathlib import Path
import requests
import os
import subprocess
from google.cloud import storage
from pathlib import Path

import uuid
import shutil
from .init_bucket import create_bucket_class_location,upload_blob
from datasets import load_dataset
# import kaggle
from datasets import load_dataset_builder
# from ...ansible_main.cloud_init import cloud_init_gen

# to update run pip install -e .

# Declared globally at the top so it can be easily modified
cred_path = Path(__file__).parent.parent.parent / 'creds'
# requirements_path =
# output_path =
docker_vars_path = Path(__file__).parent.parent.parent / \
    'ansible_main' / 'ansible_control' / 'vars.yml'
requirements_path = Path(__file__).parent.parent.parent / \
    'ansible_main' / 'cloud_init' / 'requirements.txt'


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
        (new_directory_path / 'terraform').mkdir(parents=True, exist_ok=True)
        (new_directory_path / '.kaggle').mkdir(parents=True, exist_ok=True)
        print("Directories successfully created!")
    except Exception as error:
        print(f"Error creating project: {error}")

# Prepare the data and src directories within the parent directory and build their images
# creating a Dockerfile for each if one does not exist already, the Dockerfile
# is currenlty very hardcoded and will need to either be made dynamic
# or handled elsewhere (Ansible) later


def prepare_project(project_path):#generate docker image for data and src, upload to bucket_name
    requirements_path = "/opt/anaconda3/lib/python3.12/ansible_main/cloud_init/requirements.txt"
    bucket_name = f"test-bucket-{uuid.uuid4()}"  # unique bucket name
    project_path = Path(project_path)
    
    if not project_path.is_dir():
        print(f"Error: '{project_path}' is not a valid directory")
        return

    # Paths for src and data directories
    project_path_data = project_path / 'data'
    project_path_src = project_path / 'src'
    
    # Generate requirements.txt
    if project_path_src.is_dir():
        try:
            subprocess.run(
                ['pipreqs', str(project_path_src), '--savepath', str(requirements_path)],
                check=True
            )
            print(f"Requirements file saved at {requirements_path}")
        except subprocess.CalledProcessError as error:
            print(f"Error generating requirements.txt: {error}")
            return
    else:
        print(f"Error: '{project_path_src}' directory does not exist")
        return

    # Build Docker images for data and src directories
    for dir_name in ['data', 'src']:
        dir_path = project_path / dir_name
        dockerfile_path = dir_path / 'Dockerfile'
        
        # Ensure Dockerfile exists
        if not dockerfile_path.exists():
            with open(dockerfile_path, 'w') as f:
                f.write("FROM alpine:latest\n")
        
        # Build Docker image
        image_name = dir_name
        try:
            print(f"Building Docker image '{image_name}'...")
            subprocess.run(['docker', 'build', '-t', image_name, str(dir_path)], check=True)
            print(f"Image '{image_name}' built successfully")
        except subprocess.CalledProcessError as error:
            print(f"Error building Docker image '{image_name}': {error}")
            return
        
        # Save Docker image as .tar file
        tar_path = project_path / f"{image_name}.tar"
        try:
            print(f"Saving Docker image '{image_name}' as '{tar_path}'...")
            subprocess.run(['docker', 'save', '-o', str(tar_path), image_name], check=True)
            print(f"Image '{image_name}' saved as '{tar_path}'")
        except subprocess.CalledProcessError as error:
            print(f"Error saving Docker image '{image_name}': {error}")
            return

        create_bucket_class_location(bucket_name)
        # Upload .tar file to GCS using upload_blob
        upload_blob(bucket_name, str(tar_path), f"docker-images/{image_name}.tar")

    # Upload requirements.txt to GCS
    upload_blob(bucket_name, str(requirements_path), "requirements/requirements.txt")



# def prepare_project(project_path):
#     # create bucket using uuid
#     bucket_name = f"test-bucket-{uuid.uuid4()}" 
#     destination_blob_name_data = "dockerimages/data/Dockerfile"
#     destination_blob_name_src = "dockerimages/src/Dockerfile"
#     destination_blob_name_req = "dockerimages/src/requirements.txt"
#     requirements_path = "/opt/anaconda3/lib/python3.12/ansible_main/cloud_init/requirements.txt"
#     create_bucket_class_location(bucket_name)

#     # The parent directory
#     project_path = Path(project_path)

#     if not project_path.is_dir():
#         print(f"Error: '{project_path}' is not a valid directory")
#         return

#     project_path_data = project_path / 'data'
#     project_path_src = project_path / 'src'

#     if project_path_src.is_dir():
#         try:
#             subprocess.run(['pipreqs', str(project_path_src),
#                            '--savepath', str(requirements_path)], check=True)
#         except subprocess.CalledProcessError as error:
#             print(f"Error generating requirements.txt: {error}")
#     else:
#         print(f"Error: '{project_path_src}' directory does not exist")

#     # Creates Data Dockerfile
#     dockerfile_path_data = project_path_data / 'Dockerfile'

#     if not dockerfile_path_data.exists():
#         with open(dockerfile_path_data, 'w') as f:
#             f.write("FROM alpine:latest\n")

#     try:
#         image_name_data = project_path_data.name
#         print(f"building Docker image '{image_name_data}'...")
#         subprocess.run(['docker', 'build', '-t', image_name_data,
#                        str(project_path_data)], check=True)
#         print(f"image '{image_name_data}' built successfully")
#         project_push(image_name_data)

#     except subprocess.CalledProcessError as error:
#         print(f"Error: {error}")

#     # Creates Src Dockerfile
#     dockerfile_path_src = project_path_src / 'Dockerfile'

#     if not dockerfile_path_src.exists():
#         with open(dockerfile_path_src, 'w') as f:
#             f.write("FROM alpine:latest\n")

#     try:
#         image_name_src = project_path_src.name
#         print(f"building Docker image '{image_name_src}'...")
#         subprocess.run(['docker', 'build', '-t', image_name_src,
#                        str(project_path_src)], check=True)
#         print(f"image '{image_name_src}' built successfully")
#         project_push(image_name_src)

#     except subprocess.CalledProcessError as error:
#         print(f"Error: {error}")

#     docker_yaml_create(image_name_src, image_name_data)

#     # cloud_init_gen.generate_cloud_init_yaml(requirements_path, output_path, image_name_src, image_name_data)

#     #upload to gsc buckets
#     upload_blob(bucket_name, project_path_data/"Dockerfile", destination_blob_name_data)
#     upload_blob(bucket_name, project_path_src/"Dockerfile", destination_blob_name_src)
#     upload_blob(bucket_name, requirements_path, destination_blob_name_req)
#     # return bucket_name


def docker_yaml_create(image_name_src="src", image_name_data="data"):
    docker_yaml = f'''# vars.yml
    artifact_src: "/Users/guzhaowen/orchestrating-ai-app-cloud/ansible_main/ansible_control/artifact-reader.json"
    artifact_dest: "/tmp/artifact-reader.json"
    docker_image_name_src: "us-east4-docker.pkg.dev/cynthusgcp-438617/cynthus-images/{image_name_src}"
    docker_image_name_data: "us-east4-docker.pkg.dev/cynthusgcp-438617/cynthus-images/{image_name_data}"
    docker_image_tag: "latest"
    gcp_repo_location: "us-east4"
    '''
    with open(docker_vars_path, "w") as f:
        f.write(docker_yaml)

# Start a Google Cloud VM Instance.


def project_vm_start(project_path):

    # The parent directory
    project_path = Path(project_path)
    project_mainfile = project_path/'main.tf'

    if not project_mainfile.exists():
        print(f"Error: '{project_mainfile}' does not exist.")
        return

    # Initializes Terraform
    try:
        print(f"Starting VM instance...\n")
        subprocess.run(['terraform', 'init'], check=True)
        print("Success!\n")

    except subprocess.CalledProcessError as error:
        print(f"Error: {error}")

    # Plans Terraform
    try:
        print(f"Planning Terraform...\n")
        subprocess.run(['terraform', 'plan'], check=True)
        print("Success!\n")

    except subprocess.CalledProcessError as error:
        print(f"Error: {error}")

    # Applies Terraform Configuration

    try:
        print(f"Applying Terraform Configuration...\n")
        subprocess.run(['terraform', 'apply'], check=True)
        print("Success!\n")

    except subprocess.CalledProcessError as error:
        print(f"Error: {error}")

# Start a Google Cloud VM Instance.


def project_vm_end():

    # Destorys VM
    try:
        print(f"Ending VM instance...\n")
        subprocess.run(['terraform', 'destroy'], check=True)
        print("Success!\n")

    except subprocess.CalledProcessError as error:
        print(f"Error: {error}")


# Pushes the specified image to the specified container registry
# currently deadlocked on intel by our inability to access Intel API and SSH implementation

def project_push(image_name):
    # gcp_docker_auth()
    subprocess.run(["docker", "tag", str(
        image_name), f"us-east4-docker.pkg.dev/cynthusgcp-438617/cynthus-images/{image_name}"])

    subprocess.run(
        ["docker", "push", f"us-east4-docker.pkg.dev/cynthusgcp-438617/cynthus-images/{image_name}"])


# UNIMPLEMENTED
# Auth the user into a specified cloud service using the supported login method, supported
# platforms include: ()


def gcp_docker_auth():
    docker_login_command = ['docker', 'login', '-u', '_json_key',
                            '--password-stdin', 'https://us-east4-docker.pkg.dev']
    if os.name == 'nt':  # Windows
        command = "Get-Content cynthusgcp-registry.json"
        ps_command = ['powershell', '-Command', command]
        with subprocess.Popen(ps_command, cwd=cred_path, stdout=subprocess.PIPE) as ps_proc:
            subprocess.run(docker_login_command, stdin=ps_proc.stdout)

    else:  # (Linux/Mac)
        cat_command = ['cat', 'cynthusgcp-registry.json']
        with subprocess.Popen(cat_command, cwd=cred_path, stdout=subprocess.PIPE) as cat_proc:
            subprocess.run(docker_login_command, stdin=cat_proc.stdout)


# Loads a dataset into the data container

def project_datapull(location_type, location):

    # Path declarations
    project_path = Path(project_path)
    if not project_path.is_dir():
        print(f"Error: '{project_path}' is not a valid directory")
        return
    project_path_data = project_path / 'data'

    # Local datasets
    if location_type == "local_path":
        try:
            shutil.move(location, project_path_data)
            print("All files moved successfully.")
        except shutil.Error as e:
            print("Error moving files:", e)
        except Exception as e:
            print("Unexpected error:", e)

    # Public datasets
    elif location_type == 'url':
        key = location.split("datasets/", 1)

        # Kaggle datasets
        if "kaggle.com" in location:
            try:
                # Check if Kaggle API key is set
                if not os.path.exists(os.path.expanduser("~/.kaggle/kaggle.json")):
                    print("Kaggle API key is not set. Please set it up.")
                    return

                # Download dataset
                kaggle.api.dataset_download_files(
                    key, path=project_path_data, unzip=True)
            except Exception as error:
                print(f"Error downloading Kaggle dataset: {error}")

        # Hugging Face datasets
        elif "huggingface.co" in location:
            try:
                dataset = load_dataset(key)
                dataset.save_to_disk(project_path_data)
            except Exception as error:
                print(f"Error downloading Hugging Face dataset: {error}")

    # Argument errors
    else:
        print(f"Error: '{type}' is not a valid type")
        return

    # Calculate dataset size
    try:
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(project_path_data):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)

        total_size_mb = total_size / (1024 * 1024)
        print(f"Dataset '{key}' downloaded to '{project_path_data}'")
        print(f"Total size: {total_size_mb:.2f} MB")
    except Exception as error:
        print(f"Error calculating dataset size: {error}")


def cli_entry_point():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    parser_ping = subparsers.add_parser('ping', help='Ping intel site')

    parser_print = subparsers.add_parser('print', help='Print help message')

    parser_info = subparsers.add_parser('info', help='Get VM package info')

    # Initialize a project directory

    parser_init = subparsers.add_parser('init', help='Create Cynthus project')
    parser_init.add_argument(
        'project_name',
        help='The name of the project to create'
    )

    # Command to prepare the components of a parent directory

    parser_prepare = subparsers.add_parser(
        'prepare', help='Prepare and push a project directory to the GCP')
    parser_prepare.add_argument(
        'project_path',
        help='The path to the project directory to prepare'
    )

    # Start a VM instance
    # Currently set up for Google Cloud

    parser_VM_start = subparsers.add_parser(
        'VM_start', help='Start a VM instance')
    parser_VM_start.add_argument(
        'project_path',
        help='The path to the terraform main.tf file to start the VM'
    )

    # End VM instance
    # Currently set up for Google Cloud

    parser_VM_end = subparsers.add_parser('VM_end', help='End VM instance')

    # parser_push = subparsers.add_parser(
    #     'push', help='Push a specified image to a specified cloud registry')
    # parser_push.add_argument(
    #     'image_path',
    #     help='The image to prepare'
    # )
    # parser_push.add_argument(
    #     'registry',
    #     help='The name of the registry'
    # )

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
        'datapull', help='Source a dataset from a local path or supported API')
    parser_datapull.add_argument(
        'location_type',
        help='local_path or url'
    )
    parser_datapull.add_argument(
        'location',
        help='The local path or url to pull data from'
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

    parser_gcp_docker_auth = subparsers.add_parser(
        'gcp-docker-auth', help='Authenticate to GCP Artifact Registry (test command)')

    parser_docker_yaml_create = subparsers.add_parser(
        'docker-yaml-create', help='Create sample yaml file (test command)')

    args = parser.parse_args()

    if args.command == 'ping':
        ping_intel()
    elif args.command == 'upload':
        model_upload()
    elif args.command == 'info':
        give_info()
    elif args.command == 'init':
        init_project(args.project_name)
    elif args.command == 'VM_start':
        project_vm_start(args.project_path)
    elif args.command == 'VM_end':
        project_vm_end()
    elif args.command == 'prepare':
        prepare_project(args.project_path)
    # elif args.command == 'push':
    #     project_push(args.image_path, args.registry)
    # elif args.command == 'ssh':
    #     project_ssh(args.ssh_key, args.service)
    elif args.command == 'datapull':
        project_datapull(args.location_type, args.location)
    elif args.command == 'setup_kaggle':
        setup_kaggle()
    elif args.command == 'download-kaggle':
        download_kaggle_dataset(args.dataset, args.dest_path)
    elif args.command == 'gcp-docker-auth':
        gcp_docker_auth()
    elif args.command == 'docker-yaml-create':
        docker_yaml_create()
    else:
        parser.print_help()
