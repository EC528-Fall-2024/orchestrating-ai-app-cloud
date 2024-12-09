# Cynthus CLI

Cynthus CLI is a Command Line Interface (CLI) tool designed for deploying AI applications on the cloud. It provides a streamlined process for setting up projects, managing cloud resources, and deploying applications using Google Cloud Platform (GCP).

## Features

- **Authentication**: Secure user authentication using Firebase.
- **Project Initialization**: Create a structured project directory with necessary configurations.
- **Project Preparation**: Prepare and push project directories to GCP, including Docker image creation and upload.
- **VM Management**: Start and stop VM instances using Terraform.
- **Data Management**: Upload and manage datasets from local or external sources.
- **Resource Management**: Destroy resources when no longer needed to save costs.

## Usage

Cynthus provides several commands to manage your cloud-based AI projects:

### Authentication

- **Sign Up**: Create a new Cynthus account.
  ```bash
  cynthus signup
  ```

- **Log In**: Log in to your existing Cynthus account.
  ```bash
  cynthus login
  ```

### Project Management

- **Initialize Project**: Create a new project directory.
  ```bash
  cynthus init <project_name>
  ```

- **Prepare Project**: Prepare and push a project directory to GCP.
  ```bash
  cynthus prepare --src_path <src_directory> [--data_path <data_directory>]
  ```

### Data Management

- **Update Data**: Push new or updated data to the cloud.
  ```bash
  cynthus update-data
  ```

- **Update Source Code**: Push updated source code to the artifact registry.
  ```bash
  cynthus update-src
  ```

### VM Management

- **Run Container**: Run the container associated with the user.
  ```bash
  cynthus run
  ```

- **Destroy Resources**: Destroy the current resources.
  ```bash
  cynthus destroy
  ```

### Output Management

- **Pull Output**: Pull output bucket contents to a local directory.
  ```bash
  cynthus pull
  ```

## Code Structure

- **`cynthus/project_setup.py`**: Functions for setting up and preparing projects.
  - `init_project`: Initializes the project directory.
  - `prepare_project`: Prepares the project for deployment.
  - `src_update`: Updates the source code directory.
  - `project_push`: Pushes Docker images to the registry.
  - `startLine: 43`
  - `endLine: 151`

- **`cynthus/bucket_ops.py`**: Operations related to GCS bucket management.
  - `create_bucket`: Creates a new bucket.
  - `upload_file`: Uploads files to the bucket.
  - `do_bucket_operations`: Handles bucket operations for a directory.
  - `startLine: 9`
  - `endLine: 134`

- **`cynthus/firebase_auth.py`**: Handles user authentication with Firebase.
  - `sign_up_user`: Signs up a new user.
  - `login_user`: Logs in an existing user.
  - `check_authentication`: Checks if a user is authenticated.
  - `startLine: 12`
  - `endLine: 99`

- **`cynthus/commands.py`**: CLI command definitions and entry point.
  - `cli_entry_point`: Main entry point for the CLI.
  - `startLine: 11`
  - `endLine: 107`

## Dependencies

- `requests`
- `pathlib`
- `urllib3`

## Authors

- Ryan Darrow
- Krishna Patel
- Thai Nguyen
- Zhaowen Gu
- Harlan Jones
- Jialin Sui
