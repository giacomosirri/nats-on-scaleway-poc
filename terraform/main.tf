provider "scaleway" {
  project_id      = "d43489e8-6103-4cc8-823b-7235300e81ec"
  organization_id = "daf36079-e52c-416c-9535-d06742e48acc"
  region          = "fr-par"
  zone  	        = "fr-par-1"
}

module "kubernetes_module" {
  source = "./kubernetes-module"
  cluster_name = "data-aggr-k8s-cluster-${var.app_name}"
}

resource "scaleway_mnq_nats_account" "main" {
  name        = "nats-${var.app_name}"
}

resource "scaleway_rdb_instance" "main" {
  name           = "db-${var.app_name}"
  node_type      = "DB-DEV-S"
  engine         = "PostgreSQL-15"
  is_ha_cluster  = true
  disable_backup = true
  user_name      = "my_initial_user"
  password       = "thiZ_is_v&ry_s3cret"
}

resource "scaleway_rdb_database" "main" {
  instance_id    = scaleway_rdb_instance.main.id
  name           = "test-db-instance"
}