#!/bin/bash

sudo docker compose -f docker_cloud_init.yaml build

sudo docker compose -f docker_cloud_init.yaml up

# Build the Docker images
sudo docker compose -f docker_terraform_compose.yaml build

# Initialize Terraform
sudo docker compose -f docker_terraform_compose.yaml run --rm terraform init

# Plan Terraform changes
sudo docker compose -f docker_terraform_compose.yaml run --rm terraform plan

# Optionally, you can add the apply command here if you want to run it as well
sudo docker compose -f docker_terraform_compose.yaml run --rm terraform apply -auto-approve

sleep 60
ansible-playbook -i /home/control/control-ansible/cynthus.gcp.yml /home/control/control-ansible/playbook.yml