resource "random_id" "rid" {
  byte_length = 3
}

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
  name  = "cynthus-compute-disk-${random_id.rid.dec}"
  type  = "pd-standard"
  zone  = var.zone
  size  = 10 // Size in GB
}

resource "google_compute_instance" "default" {
  name         = "cynthus-compute-instance-${random_id.rid.dec}"
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

  labels = {
    role        = "managed"
    environment = "development"
  }

  tags = ["cynthus-compute-instance-${random_id.rid.dec}", "http-server", "https-server", "ssh-server"]
}

resource "google_compute_firewall" "rules" {
  project     = var.project_id
  name        = "cynthus-compute-instance-${random_id.rid.dec}"
  network     = "default"
  description = "Allows access to OPEA AI ChatQnA"

  allow {
    protocol = "tcp"
    ports    = ["80", "443", "6379", "8001", "6006", "6007", "6000", "7000", "8808", "8000", "8888", "5173", "5174", "9009", "9000"]
  }
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["cynthus-compute-instance-${random_id.rid.dec}"]
}

output "instance_ip" {
  value = google_compute_instance.default.network_interface[0].access_config[0].nat_ip
}
