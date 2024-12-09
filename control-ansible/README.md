# Project Overview

This control node component uses Ansible to automate the provisioning, updating, and management of Docker containers on Google Cloud Platform (GCP) using Ansible and FastAPI. It includes several Ansible playbooks and a FastAPI application to facilitate these operations.

## Components

### Ansible Playbooks

1. **Provisioning Playbook (`provision.yml`)**:
   - Installs Docker and other dependencies on target instances.
   - Copies necessary service account files to the target instance.
   - References:     ```yaml:provision.yml
     startLine: 1
     endLine: 35     ```

2. **Code Update Playbook (`code-update.yml`)**:
   - Updates the code on the target instance by pulling the latest Docker image from the GCP Artifact Registry.
   - References:     ```yaml:code-update.yml
     startLine: 1
     endLine: 29     ```

3. **Data Update Playbook (`data-update.yml`)**:
   - Manages data updates by removing old data directories and downloading new datasets from Google Cloud Storage.
   - References:     ```yaml:data-update.yml
     startLine: 1
     endLine: 30     ```

4. **Container Run Playbook (`container-run.yml`)**:
   - Manages the execution of Docker containers, including log management and notification via a cloud function.
   - References:     ```yaml:container-run.yml
     startLine: 1
     endLine: 43     ```

### FastAPI Application

- The FastAPI application provides endpoints to trigger the Ansible playbooks for provisioning, code updates, data updates, and running containers.
- Key endpoints include:
  - `/provision`: Provisions a new instance.
  - `/code-update`: Updates the code on an existing instance.
  - `/data-update`: Updates data on an existing instance.
  - `/run`: Runs a Docker container on the instance.
- References:  ```python:ansible-instance.py
  startLine: 1
  endLine: 340  ```

### Configuration Files

- **Ansible Configuration (`ansible.cfg`)**:
  - Configures Ansible to use specific plugins and Python interpreter.
  - References:    ```ansible.cfg
    startLine: 1
    endLine: 6    ```

- **Variables File (`vars.yml`)**:
  - Contains variable definitions used across playbooks.
  - References:    ```yaml:vars.yml
    startLine: 1
    endLine: 10    ```

### Additional Scripts and Services

- **Systemd Service (`control-ansible.service`)**:
  - Manages the FastAPI application as a systemd service.
  - References:    ```systemd/control-ansible.service
    startLine: 1
    endLine: 14    ```

- **Google Cloud Function (`get-private-ip/main.py`)**:
  - Retrieves the private IP address of a GCP instance.
  - References:    ```python:get-private-ip/main.py
    startLine: 1
    endLine: 46    ```

## Getting Started

1. **Setup Environment**:
   - Ensure all dependencies are installed as per `requirements.txt`.
   - Configure GCP credentials and environment variables.

2. **Deploy FastAPI Application**:
   - Use the provided systemd service file to manage the FastAPI application.

3. **Run Ansible Playbooks**:
   - Use the FastAPI endpoints to trigger the desired playbooks.

