#########################################################################################

# This section includes functions that help set-up a user project. The functions include:
# - init_project(project_name)
# - prepare_project(src_path, data_path)
# - docker_yaml_create(image_name_src="src", image_name_data="data")
# - project_push(image_name)

#########################################################################################

# from docker_ops import do_docker_ops
# from bucket_ops import do_bucket_operations
from pathlib import Path
import subprocess
import json
from .init_bucket import create_bucket_class_location, upload_blob
from . import firebase_auth
from .bucket_ops import *
from .docker_ops import *


def create_config(config_path):

    config_path_file = config_path / 'config.json'

    # Create a dictionary to store the data
    data = {
        "machine_type": "e2-medium",
        "disk_size": 30,
    }

    with open(config_path_file, "w") as outfile:
        json.dump(data, outfile)

# Initializes the project with the following directory strcuture. 
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


def _process_src_directory(src_path):
    """Helper function to process source directory"""
    # Create Dockerfile if it doesn't exist
    dockerfile_path = src_path / 'Dockerfile'
    if not dockerfile_path.exists():
        with open(dockerfile_path, 'w') as f:
            f.write("FROM alpine:latest\n")

    # Build Docker image
    image_name = 'src_image'
    try:
        print(f"Building Docker image '{image_name}'...")
        subprocess.run(['docker', 'build', '-t', image_name,
                       str(src_path)], check=True)
        print(f"Image '{image_name}' built successfully")
        return image_name
    except subprocess.CalledProcessError as error:
        print(f"Error building Docker image '{image_name}': {error}")
        return None


def _process_data_directory(data_path, bucket_name, tar_data):
    """Helper function to process data directory"""
    if tar_data:
        return _handle_tarred_data(data_path, bucket_name)
    else:
        return _handle_individual_files(data_path, bucket_name)


def _handle_tarred_data(data_path, bucket_name):
    """Helper function to handle tarred data upload"""
    data_tar_path = data_path.with_suffix('.tar')
    try:
        print(f"Tarring data directory to '{data_tar_path}'...")
        subprocess.run(['tar', '-cf', str(data_tar_path), '-C',
                       str(data_path.parent), data_path.name], check=True)
        print(f"Data tar file '{data_tar_path}' created successfully")
        upload_blob(bucket_name, str(data_tar_path), "data/data.tar")
        return True
    except subprocess.CalledProcessError as error:
        print(f"Error creating tar file for data directory: {error}")
        return False


def _handle_individual_files(data_path, bucket_name):
    """Helper function to handle individual file uploads"""
    try:
        for file_path in data_path.rglob('*'):
            if file_path.is_file():
                blob_path = f"data/{file_path.relative_to(data_path)}"
                upload_blob(bucket_name, str(file_path), blob_path)
        return True
    except Exception as error:
        print(f"Error uploading individual files: {error}")
        return False


def docker_yaml_create(image_name_src="src", image_name_data="data"):
    """Create Docker YAML configuration file"""
    docker_yaml = f'''# vars.yml
    artifact_src: "/home/control/cynthus/orchestrating-ai-app-cloud/ansible_main/ansible_control/artifact-reader.json"
    artifact_dest: "/tmp/artifact-reader.json"
    docker_image_name_src: "us-east4-docker.pkg.dev/cynthusgcp-438617/cynthus-images/{image_name_src}"
    docker_image_name_data: "us-east4-docker.pkg.dev/cynthusgcp-438617/cynthus-images/{image_name_data}"
    docker_image_tag: "latest"
    gcp_repo_location: "us-east4"
    '''
    # with open(docker_vars_path, "w") as f:
    #     f.write(docker_yaml)

# Pushes the specified image to the specified container registry
# Inputs:
# -
# currently deadlocked on intel by our inability to access Intel API and SSH implementation


def project_push(image_name):
    # gcp_docker_auth()
    subprocess.run(["docker", "tag", str(
        image_name), f"us-east4-docker.pkg.dev/cynthusgcp-438617/cynthus-images/{image_name}"])

    subprocess.run(
        ["docker", "push", f"us-east4-docker.pkg.dev/cynthusgcp-438617/cynthus-images/{image_name}"])

