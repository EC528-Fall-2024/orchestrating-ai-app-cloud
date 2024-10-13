provider "google" {
  project = "cynthus-project" #change to project ID on GCP
  region  = "us-central1"
}

resource "google_compute_instance" "vm_instance" {
  name         = "control-node-instance"
  machine_type = "e2-micro"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts" 
    }
  }

  network_interface {
    network = "default"
    access_config {}
  }

  metadata = {
    user-data = file("${path.module}/control_cloudinit.yaml") 
  }

  tags = ["control"]

}

output "instance_ip" {
  value = google_compute_instance.vm_instance.network_interface.0.access_config.0.nat_ip
}

