# Terraform main configuration
MAIN_TF = '''
terraform {
  backend "gcs" {
    bucket = "terraform-state-cynthus"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = "us-east4"
  zone    = var.zone
}

resource "google_compute_instance" "default" {
  name         = var.instance_name
  machine_type = var.machine_type
  zone         = var.zone

  metadata = {
    user-data = templatefile(var.cloud_init_config, {})
  }
  
  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = var.disk_size
    }
  }

  network_interface {
    network = var.network
    access_config {}
  }

  labels = var.labels
  tags   = var.tags
}

resource "google_compute_firewall" "rules" {
  project     = var.project_id
  name        = var.instance_name
  network     = var.network
  description = "Allows access to services"

  allow {
    protocol = "tcp"
    ports    = var.firewall_ports
  }
  source_ranges = ["0.0.0.0/0"]
  target_tags   = var.tags
}

output "instance_ip" {
  value = google_compute_instance.default.network_interface[0].access_config[0].nat_ip
}
'''

# Terraform variables configuration
VARIABLES_TF = '''
variable "zone" {
  description = "The zone where resources will be created"
  type        = string
}

variable "project_id" {
  description = "The project ID to use for the resources"
  type        = string
}

variable "instance_name" {
  description = "Name of the compute instance"
  type        = string
}

variable "machine_type" {
  description = "Machine type for the compute instance"
  type        = string
  default     = "e2-medium"
}

variable "disk_size" {
  description = "Boot disk size in GB"
  type        = number
  default     = 100
}

variable "network" {
  description = "Network to deploy to"
  type        = string
  default     = "default"
}

variable "labels" {
  description = "Labels to apply to the instance"
  type        = map(string)
}

variable "tags" {
  description = "Network tags to apply to the instance"
  type        = list(string)
}

variable "firewall_ports" {
  description = "List of ports to allow in firewall"
  type        = list(string)
}

variable "cloud_init_config" {
  description = "Path to cloud-init configuration file"
  type        = string
}

'''