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

#Random ID to minimize the chances of name conflicts
resource "random_id" "rid" {
  byte_length = 3
}

#Required firewall rules
resource "google_compute_firewall" "rules" {
  project     = var.project
  name        = "ai-opea-chatqna-${random_id.rid.dec}"
  network     = "default"
  description = "Allows access to OPEA AI ChatQnA"

  allow {
    protocol = "tcp"
    ports    = ["80", "443", "6379", "8001", "6006", "6007", "6000", "7000", "8808", "8000", "8888", "5173", "5174", "9009", "9000"]
  }
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["ai-opea-chatqna-${random_id.rid.dec}"]
}

output "instance_ip" {
  value = google_compute_instance.default.network_interface[0].access_config[0].nat_ip
}
