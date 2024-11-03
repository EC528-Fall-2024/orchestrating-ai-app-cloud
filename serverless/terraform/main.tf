resource "random_id" "rid" {
  byte_length = 3
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
    user-data = file(var.cloud_init_config)
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