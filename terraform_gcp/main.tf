provider "google" {
  project = var.project_id
  region  = "us-east4"
  zone    = var.zone
}

data "template_file" "dockerfile" {
  template = file("/terraform/Dockerfile")
}

data "template_file" "cloud_init" {
  template = file("/terraform/cloud-init-config.yaml")
  vars = {
    ssh_public_key = var.ssh_public_key
  }
}

resource "google_compute_disk" "data" {
  name = "disk-data"
  type = "pd-standard"
  zone = var.zone
  size = "10" # GB
}

resource "google_compute_disk" "src" {
  name = "disk-src"
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
    source      = google_compute_disk.data.id
    device_name = google_compute_disk.data.name
  }
  attached_disk {
    source      = google_compute_disk.src.id
    device_name = google_compute_disk.src.name
  }

  network_interface {
    network = "default"
    access_config {
      // Ephemeral public IP
    }
  }

  metadata = {
    user-data = data.template_file.cloud_init.rendered
    dockerfile = data.template_file.dockerfile.rendered
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
