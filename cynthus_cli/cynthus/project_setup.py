#########################################################################################

# This section includes functions that help set-up a user project. The functions include:
# - init_project(project_name)
# - prepare_project(src_path, data_path)
# - docker_yaml_create(image_name_src="src", image_name_data="data")
# - project_push(image_name)

#########################################################################################
from pathlib import Path
import subprocess
import json
from . import firebase_auth
from .bucket_ops import *
from .docker_ops import *
from .datapull import *
import sys


def create_config(config_path):

    config_path_file = config_path / 'config.json'

    # Create a dictionary to store the data
    data = {
        "machine_type": "e2-medium",
        "disk_size": 30,
    }

    with open(config_path_file, "w") as outfile:
        json.dump(data, outfile)

# Initializes the project with the following directory strcuture
# project |
#         - src
#         - data
#         - config
#
# Note that this will create the directory in the location where this command is called



def init_project(project_name):
    current_path = Path.cwd()
    new_directory_path = current_path / project_name

    try:
        new_directory_path.mkdir(parents=True, exist_ok=True)

        # create config file in root project directory
        create_config(new_directory_path)

        (new_directory_path / 'data').mkdir(parents=True, exist_ok=True)
        (new_directory_path / 'src').mkdir(parents=True, exist_ok=True)
        print("Directories successfully created!")
    except Exception as error:
        print(f"Error creating project: {error}")

# Prepare the data and src directories within the parent directory and build their images
# creating a Dockerfile for each if one does not exist already, the Dockerfile
# is currenlty very hardcoded and will need to either be made dynamic
# or handled elsewhere (Ansible) later


def prepare_project(src_path, data_path):
    """
    Prepare project directories by creating Docker images and uploading to GCS bucket.

    Args:
        src_path (str/Path): Path to source code directory
        data_path (str/Path, optional): Path to data directory. If None, skips data processing
    """
    # Get Firebase authentication
    token, uid = firebase_auth.check_authentication()
    if not token or not uid:
        print("Authentication required. Please log in first.")
        return

    # Create bucket name using new naming convention
    bucket_name = f"user-bucket-{uid}".lower()
    src_path = Path(src_path)

    # Validate src path
    if not src_path.is_dir():
        print(f"Error: '{src_path}' is not a valid directory")
        return

    # Handle data directory if provided
    if data_path:
        data_path = Path(data_path)
        if not data_path.is_dir():
            print(f"Error: '{data_path}' is not a valid directory")
            return
        try:
            do_bucket_operations(str(data_path))
        except Exception as e:
            print(f"Error uploading data directory: {e}")
            return
    else:
        print("No data directory provided. Prompting user for external data.")
        external_data()

    # Process source directory and build Docker image
    image_name = _process_src_directory(src_path)
    if not image_name:
        return

    # Push Docker image
    try:
        run_id = "0"  # 0 for testing
        do_docker_ops(run_id, image_name)
    except Exception as e:
        print(f"Error during Docker operations: {e}")
        return

    print(f"Project preparation completed. Bucket name: {bucket_name}")
    return bucket_name

def src_update():

    token, uid = firebase_auth.check_authentication()
    if not token or not uid:
        print("Authentication required. Please log in first.")
        return

    # Create bucket name using new naming convention
    bucket_name = f"user-bucket-{uid}".lower()

    source = input("New source code directory: ")

    src_path = Path(source)

    # Validate src path
    if not src_path.is_dir():
        print(f"Error: '{src_path}' is not a valid directory")
        return

    image_name = _process_src_directory(src_path)
    if not image_name:
        return

    # Push Docker image
    try:
        run_id = "0"  # 0 for testing
        do_docker_ops(run_id, image_name)
    except Exception as e:
        print(f"Error during Docker operations: {e}")
        return

    print(f"Source code update completed to bucket: {bucket_name}")
    return bucket_name


def _process_src_directory(src_path):
    """Helper function to process source directory"""
    # Create Dockerfile if it doesn't exist
    dockerfile_path = src_path / 'Dockerfile'
    if not dockerfile_path.exists():
        with open(dockerfile_path, 'w') as f:
            f.write("FROM alpine:latest\n")
            f.write("WORKDIR /src\n")
            f.write("COPY . /src\n")
            f.write("CMD [\"/bin/sh\"]\n")

    # Build Docker image
    image_name = 'src_image'

    # Check if Docker is available
    try:
        subprocess.run(['docker', '--version'], 
                      check=True, 
                      capture_output=True, 
                      text=True)
    except FileNotFoundError:
        print("Error: Docker is not installed or not found in system PATH")
        print("Please install Docker Desktop from https://www.docker.com/products/docker-desktop/")
        print("After installation, ensure Docker Desktop is running")
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("Error: Docker is installed but not running")
        print("Please start Docker Desktop and try again")
        sys.exit(1)

    # Continue with Docker build if checks pass
    try:
        subprocess.run(['docker', 'build', '-t', image_name,
                       str(src_path)], check=True)
        print(f"Image '{image_name}' built successfully")
        return image_name
    except subprocess.CalledProcessError as error:
        print(f"Error building Docker image '{image_name}': {error}")
        return None

def project_push(image_name):
    # gcp_docker_auth()
    subprocess.run(["docker", "tag", str(
        image_name), f"us-east4-docker.pkg.dev/cynthusgcp-438617/cynthus-images/{image_name}"])

    subprocess.run(
        ["docker", "push", f"us-east4-docker.pkg.dev/cynthusgcp-438617/cynthus-images/{image_name}"])
