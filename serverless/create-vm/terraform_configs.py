# Terraform main configuration
# Updated MAIN_TF configuration
MAIN_TF = '''
terraform {
  backend "gcs" {}
}

provider "google" {
  project = var.project_id
  region  = "us-east4"
  zone    = var.zone
}

# Get GKE cluster data
data "google_container_cluster" "ml_cluster" {
  name     = "cynthus-ml-cluster"
  location = "us-east4"  # Update with your cluster's region
}

# Get cluster auth token
resource "google_container_cluster_token" "ml_cluster_token" {
  cluster_id = data.google_container_cluster.ml_cluster.id
  lifetime   = "3600s"
}

resource "google_service_account" "gke_node_sa" {
  account_id   = "gke-node-sa-${var.user_id}"
  display_name = "GKE Node Service Account for ${var.instance_name}"
}

resource "google_project_iam_member" "gke_node_sa_roles" {
  for_each = toset([
    "roles/container.nodeServiceAccount",
    "roles/artifactregistry.reader",
    "roles/monitoring.metricWriter",
    "roles/logging.logWriter"
  ])
  
  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.gke_node_sa.email}"
}

resource "google_compute_instance" "default" {
  name         = var.instance_name
  machine_type = var.machine_type
  zone         = var.zone

  metadata = {
    user-data = templatefile(var.cloud_init_config, {
      CLUSTER_ENDPOINT = data.google_container_cluster.ml_cluster.endpoint,
      CLUSTER_TOKEN = google_container_cluster_token.ml_cluster_token.token,
      CLUSTER_CA_CERT = data.google_container_cluster.ml_cluster.master_auth[0].cluster_ca_certificate,
      INSTANCE_UUID = var.user_id
    })
    cluster-name     = "cynthus-ml-cluster"
    instance-uuid    = var.user_id
    cluster-endpoint = data.google_container_cluster.ml_cluster.endpoint
    cluster-token    = google_container_cluster_token.ml_cluster_token.token
    cluster-ca-cert  = data.google_container_cluster.ml_cluster.master_auth[0].cluster_ca_certificate
  }
  
  service_account {
    email  = google_service_account.gke_node_sa.email
    scopes = ["cloud-platform"]
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

  labels = merge(var.labels, {
    "gke-cluster" = "cynthus-ml-cluster"
  })
  
  tags = concat(var.tags, ["gke-node", "cynthus-ml-${var.user_id}"])
}
'''

# Terraform variables configuration
VARIABLES_TF = '''
variable "user_id" {
  description = "The UUID of the instance"
  type        = string
}

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