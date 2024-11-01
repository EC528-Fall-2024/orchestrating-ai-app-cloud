variable "zone" {
  description = "The zone where resources will be created"
  type        = string
}

variable "ssh_public_key" {
  description = "The Ed25519 public SSH key to add to the instance"
  type        = string
}

variable "project_id" {
  description = "The project ID to use for the resources"
  type        = string
}
