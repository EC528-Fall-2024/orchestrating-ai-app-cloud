
#########################################################################################

# This section includes functions that help set-up a user project. The functions include:
# - init_project(project_name)
# - prepare_project(project_path)
# - docker_yaml_create(image_name_src="src", image_name_data="data")
# - project_push(image_name)

#########################################################################################

from pathlib import Path
import subprocess

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
#         - .kaggle

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


def prepare_project(project_path):

    # The parent directory
    project_path = Path(project_path)

    if not project_path.is_dir():
        print(f"Error: '{project_path}' is not a valid directory")
        return

    project_path_data = project_path / 'data'
    project_path_src = project_path / 'src'

    if project_path_src.is_dir():
        try:
            subprocess.run(['pipreqs', str(project_path_src),
                           '--savepath', str(requirements_path)], check=True)
        except subprocess.CalledProcessError as error:
            print(f"Error generating requirements.txt: {error}")
    else:
        print(f"Error: '{project_path_src}' directory does not exist")

    # Creates Data Dockerfile
    dockerfile_path_data = project_path_data / 'Dockerfile'

    if not dockerfile_path_data.exists():
        with open(dockerfile_path_data, 'w') as f:
            f.write("FROM alpine:latest\n")

    try:
        image_name_data = project_path_data.name
        print(f"building Docker image '{image_name_data}'...")
        subprocess.run(['docker', 'build', '-t', image_name_data,
                       str(project_path_data)], check=True)
        print(f"image '{image_name_data}' built successfully")
        project_push(image_name_data)

    except subprocess.CalledProcessError as error:
        print(f"Error: {error}")

    # Creates Src Dockerfile
    dockerfile_path_src = project_path_src / 'Dockerfile'

    if not dockerfile_path_src.exists():
        with open(dockerfile_path_src, 'w') as f:
            f.write("FROM alpine:latest\n")

    try:
        image_name_src = project_path_src.name
        print(f"building Docker image '{image_name_src}'...")
        subprocess.run(['docker', 'build', '-t', image_name_src,
                       str(project_path_src)], check=True)
        print(f"image '{image_name_src}' built successfully")
        project_push(image_name_src)

    except subprocess.CalledProcessError as error:
        print(f"Error: {error}")

    docker_yaml_create(image_name_src, image_name_data)

    # cloud_init_gen.generate_cloud_init_yaml(requirements_path, output_path, image_name_src, image_name_data)


def docker_yaml_create(image_name_src="src", image_name_data="data"):
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