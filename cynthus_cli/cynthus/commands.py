import argparse
from pathlib import Path
import requests
import subprocess
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


def handle_print():
    print('For more info, type -h or --help.')


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
        'datapull', help='Pull data from a target supported url into a VM')
    parser_datapull.add_argument(
        'url',
        help='The url to be pulled from, supports HuggingFace and Kaggle'
    )
    parser_datapull.add_argument(
        'target',
        help='The target to send the data'
    )

    args = parser.parse_args()

    if args.command == 'ping':
        ping_intel()
    elif args.command == 'print':
        handle_print()
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
        project_ssh(args.url, args.target)
    else:
        parser.print_help()
