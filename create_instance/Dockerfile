# Use Python base image
FROM python:3.10-slim
# Set working directory
WORKDIR /app
# Copy the requirements file
COPY requirements.txt .
# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Copy the script into the container
COPY create_instance.py .
# Command to run the script
CMD ["python3", "create_instance.py"]
