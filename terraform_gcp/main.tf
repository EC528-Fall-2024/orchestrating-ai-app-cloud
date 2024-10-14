variable "zone" {
  description = "The zone where resources will be created"
  type        = string
  default     = "us-east4-a"
}

provider "google" {
  project = "cynthusgcp-438617"
  region  = "us-east4"
  zone    = var.zone
}

resource "google_compute_instance" "default" {
  name         = "ubuntu-test-instance"
  machine_type = "e2-medium"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
    }
  }

  network_interface {
    network = "default"
    access_config {
      // Ephemeral public IP
    }
  }

  metadata_startup_script = "echo 'Hello, Ubuntu!' > /tmp/hello.txt"

  tags = ["ssh-server"]
}