variable "zone" {
  description = "The zone where resources will be created"
  type        = string
}

variable "project_id" {
  description = "The project ID to use for the resources"
  type        = string
}

variable "instance_name" {
  description = "Name of the compute instance"
  type        = string
}

variable "machine_type" {
  description = "Machine type for the compute instance"
  type        = string
  default     = "e2-medium"
}

variable "disk_size" {
  description = "Boot disk size in GB"
  type        = number
  default     = 100
}

variable "network" {
  description = "Network to deploy to"
  type        = string
  default     = "default"
}

variable "labels" {
  description = "Labels to apply to the instance"
  type        = map(string)
}

variable "tags" {
  description = "Network tags to apply to the instance"
  type        = list(string)
}

variable "firewall_ports" {
  description = "List of ports to allow in firewall"
  type        = list(string)
}

variable "cloud_init_config" {
  description = "Path to cloud-init configuration file"
  type        = string
}