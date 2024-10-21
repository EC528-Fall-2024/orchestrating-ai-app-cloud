variable "zone" {
  description = "The zone where resources will be created"
  type        = string
  default     = "us-east4-a"
}

variable "ssh_public_key" {
  description = "The Ed25519 public SSH key to add to the instance"
  type        = string
  default     = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFbUbFFMOV4SKX3B5Jo/1tWXa6kNhRdLoGpQtTB7/uuG suijs@bu.edu"
}

provider "google" {
  project = "cynthusgcp-438617"
  region  = "us-east4"
  zone    = var.zone
}

data "template_file" "cloud_init" {
  template = file("${path.module}/../ansible_main/cloud-init/control_cloudinit.yaml")
  vars = {
    ssh_public_key = var.ssh_public_key
  }
}

resource "google_compute_disk" "default" {
  name = "disk-secondary"
  type = "pd-standard"
  zone = var.zone
  size = "5" # GB
}

resource "google_compute_instance" "default" {
  name         = "cloud-init-test1"
  machine_type = "e2-medium"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
    }
  }
  attached_disk {
    source      = google_compute_disk.default.id
    device_name = google_compute_disk.default.name
  }

  network_interface {
    network = "default"
    access_config {
      // Ephemeral public IP
    }
  }

  metadata = {
    user-data = data.template_file.cloud_init.rendered
  }

  tags = ["http-server", "https-server", "ssh-server"]
}

# Firewall rule to allow HTTP, HTTPS and SSH traffic
resource "google_compute_firewall" "web" {
  name    = "allow-web"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["80", "443", "22"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["http-server", "https-server", "ssh-server"]
}

output "instance_ip" {
  value = google_compute_instance.default.network_interface[0].access_config[0].nat_ip
}