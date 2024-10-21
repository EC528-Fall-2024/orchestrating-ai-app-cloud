# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY ../ansible_main/cloud-init/requirements.txt .

# Copy the Python script into the container
COPY ../ansible_main/cloud-init/cloud_init_gen.py .

# Set environment variable for output path
ENV CLOUD_INIT_OUTPUT_PATH=cloud-init-config.yaml

# Run the script when the container launches
CMD ["python", "cloud_init_gen.py"]