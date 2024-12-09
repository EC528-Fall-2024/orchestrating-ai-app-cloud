# Deployment Guide

To deploy each cloud function, navigate to the respective directory containing the `cloudbuild.yaml` file and run the `gcloud builds submit` command. This command will trigger the build and deployment process as specified in the YAML configuration.

## Prerequisites

- Ensure you have the Google Cloud SDK installed and configured on your machine.
- Authenticate with your Google Cloud account using `gcloud auth login`.
- Set the appropriate project using `gcloud config set project YOUR_PROJECT_ID`.

## Deployment Commands

1. **Deploy `create-vm` Function**

   This function is responsible for creating a new VM instance on Google Cloud with specified configurations.

   ```bash
   cd path/to/create-vm
   gcloud builds submit --config=cloudbuild.yaml
   ```

2. **Deploy `create-vm-test` Function**

   This function serves as a test version of the `create-vm` function, allowing for testing and validation of VM creation processes.

   ```bash
   cd path/to/create-vm-test
   gcloud builds submit --config=cloudbuild.yaml
   ```

3. **Deploy `destroy-resources` Function**

   This function handles the destruction of cloud resources, ensuring that all associated resources are properly cleaned up.

   ```bash
   cd path/to/destroy-resources
   gcloud builds submit --config=cloudbuild.yaml
   ```

4. **Deploy `bucket-operations` Function**

   This function manages operations related to Google Cloud Storage buckets, such as creation and file uploads.

   ```bash
   cd path/to/bucket-operations
   gcloud builds submit --config=cloudbuild.yaml
   ```

5. **Deploy `bucket-listener-vm` Function**

   This function listens for bucket creation events and triggers VM creation based on the bucket's configuration.

   ```bash
   cd path/to/bucket-listener-vm
   gcloud builds submit --config=cloudbuild.yaml
   ```

6. **Deploy `run-container` Function**

   This function is responsible for running containers on a specified infrastructure, often used for executing workloads.

   ```bash
   cd path/to/run-container
   gcloud builds submit --config=cloudbuild.yaml
   ```

7. **Deploy `data-update` Function**

   This function updates data within the cloud infrastructure, ensuring that datasets and configurations are current.

   ```bash
   cd path/to/data-update
   gcloud builds submit --config=cloudbuild.yaml
   ```

8. **Deploy `code-update` Function**

   This function updates code repositories or configurations, facilitating continuous integration and deployment processes.

   ```bash
   cd path/to/code-update
   gcloud builds submit --config=cloudbuild.yaml
   ```

9. **Deploy `email-user` Function**

   This function sends email notifications to users, typically used to inform them of completed tasks or updates.

   ```bash
   cd path/to/email-user
   gcloud builds submit --config=cloudbuild.yaml
   ```

10. **Deploy `output-ops` Function**

    This function manages operations related to output data, such as generating and storing results from computations.

    ```bash
    cd path/to/output-ops
    gcloud builds submit --config=cloudbuild.yaml
    ```

11. **Deploy `docker-operations` Function**

    This function handles Docker-related operations, such as building and pushing Docker images to a registry.

    ```bash
    cd path/to/docker-operations
    gcloud builds submit --config=cloudbuild.yaml
    ```

12. **Deploy `dataset-downloader` Function**

    This function downloads datasets from specified sources and uploads them to Google Cloud Storage for further processing.

    ```bash
    cd path/to/dataset-downloader
    gcloud builds submit --config=cloudbuild.yaml
    ```

13. **Deploy `bucket-logger` Function**

    This function logs events related to bucket operations, providing insights and audit trails for storage activities.

    ```bash
    cd path/to/bucket-logger
    gcloud builds submit --config=cloudbuild.yaml
    ```
