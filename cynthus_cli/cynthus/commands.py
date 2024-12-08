import argparse
from pathlib import Path
from .project_setup import *    
from .firebase_auth import *
from .datapull import *
from .output_ops import *
from .update_ops import *
from .destroy_ops import *

def cli_entry_point():
    # From Firebase.py
    check_authentication()

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    # Sign up a user
    parser_signup = subparsers.add_parser(
        'signup', help='Create an account')

    # Log in to established Cynthus account
    parser_login = subparsers.add_parser(
        'login', help='Log in to Cynthus account')

    # Get information regarding VM package (NOT FULLY IMPLEMENTED SO FAR)
    # parser_info = subparsers.add_parser('info', help='Get VM package info')

    # Initialize a project directory Command
    parser_init = subparsers.add_parser(
        'init', help='Create Cynthus project')
    parser_init.add_argument(
        'project_name', help='The name of the project to create')

    # Command to prepare the components of a parent directory
    parser_prepare = subparsers.add_parser(
        'prepare', help='Prepare and push a project directory to the GCP')
    parser_prepare.add_argument(
        '--src_path', help='The src directory to prepare', required=True)
    parser_prepare.add_argument(
        '--data_path', help='The data directory to prepare (optional)', default=None)

    # Add new data from a local directory
    parser_updatedata = subparsers.add_parser(
        'update-data', help='Push new/updated data to bucket')
    
    # Add new source code to artifact registry
    parser_updatesrc = subparsers.add_parser(
        'update-src', help='Push updated src code to artifact registry')

    parser_update = subparsers.add_parser(
        'update', help='Update either the source or data after it has been prepared and pushed')
    
    group = parser_update.add_mutually_exclusive_group(required=False)
    group.add_argument('--src', action='store_true', help='Update the source')
    group.add_argument('--data', action='store_true', help='Update the data')

    parser_destroy = subparsers.add_parser(
        'destroy', help='Destroy the current resources')
    
    # Pull results from output bucket to local directory
    parser_output = subparsers.add_parser(
        'pull', help='Pull output bucket contents to local directory')

    args = parser.parse_args()

    if args.command == 'signup':
        sign_up_user()
    elif args.command == 'login':
        email = input('Account Email: ')
        password = input('Password: ')
        login_user(email, password)
    elif args.command == 'init':
        init_project(args.project_name)
    elif args.command == 'prepare':
        prepare_project(args.src_path, args.data_path)
    elif args.command == 'update':
        if args.src:
            print("Updating source...")
            update_src()
        elif args.data:
            print("Updating data...")
            update_data()
        else:
            print("Updating source and data...")
            update_src()
            update_data()
    elif args.command == 'destroy':
        destroy_resources()
    elif args.command == 'update-data':
        load_data()
    elif args.command == 'update-src':
        src_update()
    elif args.command == 'pull':
        pull_output()
    else:
        parser.print_help()