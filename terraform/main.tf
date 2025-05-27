provider "scaleway" {
  project_id      = "d43489e8-6103-4cc8-823b-7235300e81ec"
  organization_id = "daf36079-e52c-416c-9535-d06742e48acc"
  region          = "fr-par"
  zone  	        = "fr-par-1"
}

module "kubernetes_module" {
  source       = "./kubernetes-module"
  cluster_name = "data-aggr-k8s-cluster-${var.app_name}"
}

resource "scaleway_mnq_nats_account" "nats_acc" {
  name = "nats-${var.app_name}"
}

resource "scaleway_mnq_nats_credentials" "nats_creds" {
  account_id = scaleway_mnq_nats_account.nats_acc.id
}

module "database_module" {
  source               = "./database-module"
  database_server_name = "postgresql-db-${var.app_name}"
  database_name        = "sensor-data-db"
}