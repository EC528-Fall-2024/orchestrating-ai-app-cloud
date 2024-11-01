
#########################################################################################

# This section includes functions that interface with Terraform. The functions include:
# - project_vm_start(project_path)
# - project_vm_end()

#########################################################################################

from pathlib import Path
import subprocess

# Starts a Google Cloud VM Instance
# Inputs:
# - project_path (str): the location where the main.tf file for the project you want to initialize is saved

def project_vm_start(project_path):

    # The parent directory for the main.tf file
    project_path = Path(project_path)
    project_mainfile = project_path/'main.tf'

    # check to make sure the main.tf file exists
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


# Stops the most recent Google Cloud VM Instance created.

def project_vm_end():

    # Destorys VM
    try:
        print(f"Ending VM instance...\n")
        subprocess.run(['terraform', 'destroy'], check=True)
        print("Success!\n")

    except subprocess.CalledProcessError as error:
        print(f"Error: {error}")