variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "cynthusgcp-438617"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP Zone"
  type        = string
  default     = "us-central1-a"
}

variable "gke_version" {
  description = "GKE Version"
  type        = string
  default     = "1.27"  # Specify your desired GKE version
}