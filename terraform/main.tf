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

resource "scaleway_mnq_nats_account" "nats_acc" {
  name = "nats-${var.app_name}"
}

resource "scaleway_mnq_nats_credentials" "nats_creds" {
  account_id = scaleway_mnq_nats_account.nats_acc.id
}

resource "scaleway_rdb_instance" "postgre_server" {
  name           = "postgresql-db-${var.app_name}"
  tags           = ["postgresql"]

  node_type      = "DB-DEV-S"
  engine         = "PostgreSQL-15"

  is_ha_cluster  = false
  disable_backup = true
}

resource "scaleway_secret" "db_credentials" {
  name        = "db-credentials"
  description = "Information needed to access the ${scaleway_rdb_instance.postgre_server.name} database."
  tags        = ["postgresql"]

  type        = "database_credentials"
}

resource "random_password" "db_password" {
  length  = 16
  special = true
}

resource "scaleway_rdb_user" "db_admin" {
  instance_id = scaleway_rdb_instance.postgre_server.id
  name        = "admin"
  password    = random_password.db_password.result
  is_admin    = true
}

resource "scaleway_secret_version" "secret_data" {
  description = "v1"
  secret_id   = scaleway_secret.db_credentials.id
  data        = {
    engine = "postgres"
    username = scaleway_rdb_user.db_admin.name
    password = random_password.db_password.result
    host = scaleway_rdb_instance.postgre_server.load_balancer.hostname
    dbname = scaleway_rdb_instance.postgre_server.name
    port = scaleway_rdb_instance.load_balancer.port
  }
}

resource "scaleway_rdb_database" "sensor_data_db" {
  instance_id    = scaleway_rdb_instance.postgre_server.id
  name           = "sensor-data-db"
}