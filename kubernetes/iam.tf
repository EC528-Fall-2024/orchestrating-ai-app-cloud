# Create GKE Service Account
resource "google_service_account" "gke_sa" {
  account_id   = "gke-service-account"
  display_name = "GKE Service Account"
  project      = var.project_id // Add this line
}

# Grant necessary permissions
resource "google_project_iam_member" "gke_sa_container" {
  project = var.project_id
  role    = "roles/container.admin"
  member  = "serviceAccount:${google_service_account.gke_sa.email}"
}

resource "google_project_iam_member" "gke_sa_artifact_registry" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.gke_sa.email}"
}

resource "google_project_iam_member" "gke_sa_compute" {
  project = var.project_id
  role    = "roles/compute.admin"
  member  = "serviceAccount:${google_service_account.gke_sa.email}"
}