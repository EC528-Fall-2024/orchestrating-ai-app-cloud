# terraform/gke.tf
provider "google" {
    project     = var.project_id
    region      = var.region
}

resource "google_container_cluster" "cynthus_cluster" {
  name     = "cynthus-ml-cluster"
  location = var.region

  # Remove default node pool
  remove_default_node_pool = true
  initial_node_count       = 1

  network    = google_compute_network.cynthus_network.name
  subnetwork = google_compute_subnetwork.cynthus_subnet.name

  # Enable Workload Identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Network policy for security
  network_policy {
    enabled = true
    provider = "CALICO"
  }

  # Node auto-provisioning disabled as we're using custom VMs
  cluster_autoscaling {
    enabled = false
  }
}

resource "google_compute_network" "cynthus_network" {
  name                    = "cynthus-network"
  auto_create_subnetworks = false
  project                 = var.project_id // Add this line
}

// Declare the subnetwork resource
resource "google_compute_subnetwork" "cynthus_subnet" {
  name          = "cynthus-subnet"
  ip_cidr_range = "10.0.0.0/24" // Adjust the CIDR range as needed
  region        = var.region
  network       = google_compute_network.cynthus_network.name
  project       = var.project_id // Ensure this line is present
}


# Small management node pool
resource "google_container_node_pool" "management" {
  name       = "cynthus-management-pool"
  cluster    = google_container_cluster.cynthus_cluster.name
  location   = var.region
  node_count = 1
  project    = var.project_id // Add this line

  node_config {
    machine_type = "e2-medium"
    
    labels = {
      role = "management"
    }

    service_account = google_service_account.gke_sa.email
    oauth_scopes    = ["https://www.googleapis.com/auth/cloud-platform"]
  }
}