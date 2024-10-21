import argparse
from pathlib import Path
import requests
import os
import subprocess
import shutil
import kaggle
from datasets import load_dataset


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

# Containerize the data and src directories within the parent directory and build their images
# creating a Dockerfile for each if one does not exist already, the Dockerfile
# is currenlty very hardcoded and will need to either be made dynamic
# or handled elsewhere (Ansible) later


def containerize_project(project_path):

    # The parent directory
    project_path = Path(project_path)

    if not project_path.is_dir():
        print(f"Error: '{project_path}' is not a valid directory")
        return

    # Defines the directories to Dockerize for data and src
    project_path_data = project_path / 'data'
    project_path_src = project_path / 'src'

    # Creates Data Dockerfile
    dockerfile_path_data = project_path_data / 'Dockerfile'

    if not dockerfile_path_data.exists():
        with open(dockerfile_path_data, 'w') as f:
            f.write(f"FROM python:3.9\n")
            f.write(f"WORKDIR /src\n")
            f.write(f"COPY src/ .\n")

            # Removed the following because we might want to do installation through
            # Ansible and because I don't know how to dynamically locate the main
            # Python file from the user yet

            # f.write(f"RUN pip install -r requirements.txt\n")
            # f.write(f"CMD ['python', 'NAME_OF_CODE.py']")

    try:
        image_name_data = project_path_data.name
        print(f"building Docker image '{image_name_data}'...")
        subprocess.run(['docker', 'build', '-t', image_name_data,
                       str(project_path)], check=True)
        print(f"image '{image_name_data}' built successfully")

    except subprocess.CalledProcessError as error:
        print(f"Error: {error}")

    # Creates Src Dockerfile
    dockerfile_path_src = project_path_src / 'Dockerfile'

    if not dockerfile_path_src.exists():
        with open(dockerfile_path_src, 'w') as f:
            f.write(f"FROM python:3.9\n")
            f.write(f"WORKDIR /src\n")
            f.write(f"COPY src/ .\n")

    try:
        image_name_src = project_path_src.name
        print(f"building Docker image '{image_name_src}'...")
        subprocess.run(['docker', 'build', '-t', image_name_src,
                       str(project_path)], check=True)
        print(f"image '{image_name_src}' built successfully")

    except subprocess.CalledProcessError as error:
        print(f"Error: {error}")


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


# UNIMPLEMENTED
# Pushes the specified image to the specified container registry
# currently deadlocked by our inability to access Intel API and SSH implementation


def project_push(image_path, registry):
    pass
    # docker_registry = "REGISTRY_HERE"
    # subprocess.run(['docker', 'push', f'{docker_registry}/{image_name}'], check=True)
    # print(f"image successfully pushed to '{docker_registry}'")

    # except subprocess.CalledProcessError as error:
    #     print(f"Error: {error}")

# UNIMPLEMENTED
# SSH the user into a specified cloud service using their public SSH key, supported
# platforms include: ()


def project_ssh(ssh_key, service):
    pass


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
                kaggle.api.dataset_download_files(key, path=project_path_data, unzip=True)
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

    # Command to containerize the components of a parent directory

    parser_containerize = subparsers.add_parser(
        'containerize', help='Containerize a project directory')
    parser_containerize.add_argument(
        'project_path',
        help='The path to the project directory to containerize'
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

    parser_ssh = subparsers.add_parser(
        'ssh', help='SSH into a specified cloud registry')
    parser_ssh.add_argument(
        'ssh_key',
        help='The public key of the user'
    )
    parser_ssh.add_argument(
        'service',
        help='The cloud service to SSH into'
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
    elif args.command == 'containerize':
        containerize_project(args.project_path)
    elif args.command == 'push':
        project_push(args.image_path, args.registry)
    elif args.command == 'ssh':
        project_ssh(args.ssh_key, args.service)
    elif args.command == 'datapull':
        project_datapull(args.location_type, args.location)
    else:
        parser.print_help()
