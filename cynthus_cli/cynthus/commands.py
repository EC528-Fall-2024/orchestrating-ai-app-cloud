import argparse
from pathlib import Path
import requests
import os
import subprocess
from google.cloud import storage
from .project_setup import *
import uuid
import shutil
from .init_bucket import create_bucket_class_location, upload_blob
from datasets import load_dataset
# from .kaggle_funcs import *
from .terraform_funcs import *
from .project_setup import *
from .firebase_auth import *
from .datapull import *
from datasets import load_dataset_builder
# from ...ansible_main.cloud_init import cloud_init_gen

# to update run pip install -e .

# Declared globally at the top so it can be easily modified
cred_path = Path(__file__).parent.parent.parent / 'creds'

docker_vars_path = Path(__file__).parent.parent.parent / \
    'ansible_main' / 'ansible_control' / 'vars.yml'
requirements_path = Path(__file__).parent.parent.parent / \
    'ansible_main' / 'cloud_init' / 'requirements.txt'


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

    # Initialize a project directory Command

    parser_init = subparsers.add_parser(
        'init', help='Create Cynthus project')
    parser_init.add_argument(
        'project_name', help='The name of the project to create')

    # Command to prepare the components of a parent directory

    parser_prepare = subparsers.add_parser(
        'prepare', help='Prepare and push a project directory to the GCP')
    parser_prepare.add_argument(
        'src_path', help='The src directory to prepare')
    parser_prepare.add_argument(
        'data_path', help='The data directory to prepare')
    
    # Pull external data to a bucket

    parser_external_data = subparsers.add_parser(
        'external-data', help='Grab a dataset from external source')
    
    # Adding the commands to the parser

    args = parser.parse_args()

    if args.command == 'sign_up':
        sign_up_user()

    elif args.command == 'login':

        email = input('Account Email:')
        password = input('Password:')
        login_user(email, password)

    elif args.command == 'init':
        init_project(args.project_name)

    elif args.command == 'prepare':
        prepare_project(args.src_path, args.data_path)

    elif args.command =='external-data':
        external_data()

    else:
        parser.print_help()
