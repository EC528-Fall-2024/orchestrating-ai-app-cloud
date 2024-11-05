
#########################################################################################

# This section includes functions that help set-up a user project. The functions include:
# - init_project(project_name)
# - prepare_project(src_path, data_path)
# - docker_yaml_create(image_name_src="src", image_name_data="data")
# - project_push(image_name)

#########################################################################################

from pathlib import Path
import subprocess
from .init_bucket import create_bucket_class_location, upload_blob
from . import firebase_auth

# Globally declared paths put here so they can be easily modified

docker_vars_path = Path(__file__).parent.parent.parent / \
    'ansible_main' / 'ansible_control' / 'vars.yml'
requirements_path = Path(__file__).parent.parent.parent / \
    'ansible_main' / 'cloud_init' / 'requirements.txt'

# Initializes the project with the following directory strcuture
# project |
#         - src
#         - data
#         - config
#         - terraform


def init_project(project_name):
    current_path = Path.cwd()
    new_directory_path = current_path / project_name

    try:
        new_directory_path.mkdir(parents=True, exist_ok=True)
        (new_directory_path / 'config').mkdir(parents=True, exist_ok=True)
        (new_directory_path / 'data').mkdir(parents=True, exist_ok=True)
        (new_directory_path / 'src').mkdir(parents=True, exist_ok=True)
        (new_directory_path / 'terraform').mkdir(parents=True, exist_ok=True)
        print("Directories successfully created!")
    except Exception as error:
        print(f"Error creating project: {error}")

# Prepare the data and src directories within the parent directory and build their images
# creating a Dockerfile for each if one does not exist already, the Dockerfile
# is currenlty very hardcoded and will need to either be made dynamic
# or handled elsewhere (Ansible) later


def prepare_project(src_path, data_path=None, tar_data=False):
    """
    Prepare project directories by creating Docker images and uploading to GCS bucket.
    
    Args:
        src_path (str/Path): Path to source code directory
        data_path (str/Path, optional): Path to data directory. If None, skips data processing
        tar_data (bool): Whether to tar the data directory before upload
    """
    # Get Firebase authentication
    token, uid = firebase_auth.check_authentication()
    if not token or not uid:
        print("Authentication required. Please log in first.")
        return

    # Create unique bucket name using Firebase UID
    bucket_name = f"cynthus-{uid}-{uuid.uuid4().hex[:8]}"
    src_path = Path(src_path)

    # Validate src path
    if not src_path.is_dir():
        print(f"Error: '{src_path}' is not a valid directory")
        return

    # Generate and save requirements.txt
    requirements_path = src_path / 'requirements.txt'
    try:
        subprocess.run(
            ['pipreqs', str(src_path), '--savepath', str(requirements_path)],
            check=True
        )
        print(f"Requirements file saved at {requirements_path}")
    except subprocess.CalledProcessError as error:
        print(f"Error generating requirements.txt: {error}")
        return

    # Handle source directory
    if not _process_src_directory(src_path, bucket_name):
        return

    # Handle data directory if provided
    if data_path:
        data_path = Path(data_path)
        if not data_path.is_dir():
            print(f"Error: '{data_path}' is not a valid directory")
            return
        
        if not _process_data_directory(data_path, bucket_name, tar_data):
            return

    print(f"Project preparation completed. Bucket name: {bucket_name}")
    return bucket_name

def _process_src_directory(src_path, bucket_name):
    """Helper function to process source directory"""
    # Create Dockerfile if it doesn't exist
    dockerfile_path = src_path / 'Dockerfile'
    if not dockerfile_path.exists():
        with open(dockerfile_path, 'w') as f:
            f.write("FROM alpine:latest\n")

    # Build Docker image
    image_name = 'src'
    try:
        print(f"Building Docker image '{image_name}'...")
        subprocess.run(['docker', 'build', '-t', image_name,
                       str(src_path)], check=True)
        print(f"Image '{image_name}' built successfully")
    except subprocess.CalledProcessError as error:
        print(f"Error building Docker image '{image_name}': {error}")
        return False

    # Save Docker image as tar
    tar_path = src_path / f"{image_name}.tar"
    try:
        print(f"Saving Docker image '{image_name}' as '{tar_path}'...")
        subprocess.run(
            ['docker', 'save', '-o', str(tar_path), image_name], check=True)
        print(f"Image '{image_name}' saved as '{tar_path}'")
    except subprocess.CalledProcessError as error:
        print(f"Error saving Docker image '{image_name}': {error}")
        return False

    # Create bucket and upload files
    create_bucket_class_location(bucket_name)
    upload_blob(bucket_name, str(tar_path), f"docker-images/{image_name}.tar")
    upload_blob(bucket_name, str(src_path / 'requirements.txt'),
                "requirements/requirements.txt")
    return True

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
    with open(docker_vars_path, "w") as f:
        f.write(docker_yaml)

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


##### Old project_prepare code; can remove later if necessary #####

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
