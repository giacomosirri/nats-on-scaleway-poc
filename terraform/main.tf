provider "scaleway" {
  project_id      = "d43489e8-6103-4cc8-823b-7235300e81ec"
  organization_id = "daf36079-e52c-416c-9535-d06742e48acc"
  region          = "fr-par"
  zone  	        = "fr-par-1"
}

module "kubernetes_module" {
  source       = "./modules/kubernetes"
  cluster_name = "data-aggr-k8s-cluster-${var.app_name}"
}

module "database_module" {
  source        = "./modules/database"
  database_name = "telemetry-data-db"
}

module "nats_module" {
  source            = "./modules/nats"
  nats_account_name = "nats-account-${var.app_name}"
}

module "secret_module" {
  source                = "./modules/secret"
  db_connection         = module.database_module.database_connection_string
  nats_credentials_file = module.nats_module.nats_creds
}