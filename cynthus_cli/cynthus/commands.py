import argparse
from pathlib import Path
import requests
import os
import subprocess
from google.cloud import storage

import uuid
import shutil
from .init_bucket import create_bucket_class_location,upload_blob
from datasets import load_dataset
from .kaggle_funcs import *
from .terraform_funcs import *
from .project_setup import *
from .firebase_auth import *
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


def give_info():
    print('The VM package info can be found below: ')


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
# Inputs:
# - location_type:
# - location: 

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
    
    # From Firebase.py
    check_authentication()

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    # Sign up a user
    
    parser_signup = subparsers.add_parser(
        'sign_up', help='Create an account')
    
    # Log in to established Cynthus account
    
    parser_login = subparsers.add_parser(
        'login', help='Log in to Cynthus account')
 
    # Get information regarding VM package (NOT FULLY IMPLEMENTED SO FAR)
    parser_info = subparsers.add_parser('info', help='Get VM package info')

    # Initialize a project directory Command

    parser_init = subparsers.add_parser(
        'init', help='Create Cynthus project')
    parser_init.add_argument(
        'project_name', help='The name of the project to create')

    # Command to prepare the components of a parent directory

    parser_prepare = subparsers.add_parser(
        'prepare', help='Prepare and push a project directory to the GCP')

    # Start a VM instance Command

    parser_VM_start = subparsers.add_parser(
        'VM_start', help='Start a VM instance')

    # End VM instance Command 

    parser_VM_end = subparsers.add_parser('VM_end', help='End VM instance')

    # Push images to cloud registry Command

    # parser_push = subparsers.add_parser(
    #     'push', help='Push a specified image to a specified cloud registry')
    # parser_push.add_argument(
    #     'image_path', help='The image to prepare')
    # parser_push.add_argument(
    #     'registry', help='The name of the registry')

    # Authenticate User Command (Uninitialized Currently)

    parser_auth = subparsers.add_parser(
        'ssh', help='Authenticate into a specified cloud registry')
    parser_auth.add_argument(
        'ssh_key', help='The public key of the user')
    parser_auth.add_argument(
        'service', help='The cloud service to authenticate into')
    
    # Pull datasets for upload to buckets Command

    parser_datapull = subparsers.add_parser(
        'datapull', help='Source a dataset from a local path or supported API')
    parser_datapull.add_argument(
        'location_type', help='local_path or url')
    parser_datapull.add_argument(
        'location', help='The local path or url to pull data from')
    
    # Set-up Kaggle Command

    parser_setup_kaggle = subparsers.add_parser(
        'setup-kaggle', help='Provide instructions for Kaggle set-up')
    
    # Download Kaggle Dataset command (***May be removed***)

    parser_download_kaggle = subparsers.add_parser(
        'download-kaggle', help='Download dataset from Kaggle')
    parser_download_kaggle.add_argument(
        'dataset', help='The Kaggle dataset to download (e.g., username/dataset-name)')
    parser_download_kaggle.add_argument(
        'dest_path', help='The local directory where the dataset will be downloaded')
    
    # GCP Artifact Registry Authenication Command

    parser_gcp_docker_auth = subparsers.add_parser(
        'gcp-docker-auth', help='Authenticate to GCP Artifact Registry (test command)')
    
    # Create Docker YAML file Command

    parser_docker_yaml_create = subparsers.add_parser(
        'docker-yaml-create', help='Create sample yaml file (test command)')
    
    # Adding the commands to the parser

    args = parser.parse_args()

    if args.command == 'sign_up':
        
        email = input('Please provide the email you wish to use for this account:')
        password = input('Create a password for this account:')
        sign_up_user(email, password)

    elif args.command == 'login':

        email = input('Account Email:')
        password = input('Password:')
        login_user(email, password)

    elif args.command == 'info':
        give_info()
    elif args.command == 'init':
        init_project(args.project_name)
    elif args.command == 'VM_start':
        project_vm_start()
    elif args.command == 'VM_end':
        project_vm_end()
    elif args.command == 'prepare':

        src = input('Please provide the folder location for you src files:')
        data = input('please provide the folder location for your data files:')
        prepare_project(src, data, tar_data=False)

    # elif args.command == 'push':
    #     project_push(args.image_path, args.registry)
    # elif args.command == 'ssh':
    #     project_ssh(args.ssh_key, args.service)
    elif args.command == 'datapull':
        project_datapull(args.location_type, args.location)
    elif args.command == 'setup-kaggle':
        setup_kaggle()
    elif args.command == 'download-kaggle':
        download_kaggle_dataset(args.dataset, args.dest_path)
    elif args.command == 'gcp-docker-auth':
        gcp_docker_auth()
    elif args.command == 'docker-yaml-create':
        docker_yaml_create()
    else:
        parser.print_help()
