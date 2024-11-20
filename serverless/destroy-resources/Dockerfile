FROM python:3.9-slim

# Install required packages
RUN apt-get update && apt-get install -y \
    gnupg \
    software-properties-common \
    curl \
    wget \
    lsb-release

# Install Terraform using the official installation script
RUN wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list
RUN apt-get update && apt-get install -y terraform

RUN which terraform && \
    terraform --version && \
    ls -la /usr/bin/terraform && \
    echo "Terraform installation complete"

# Ensure terraform is in PATH and executable
ENV PATH="/usr/bin:${PATH}"
RUN chmod +x /usr/bin/terraform

# Install Python requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy function code
COPY . .

ENV PORT=8080
ENV PYTHONUNBUFFERED=True

CMD ["functions-framework", "--target=destroy_resources"]