# Create a Secret Manager instance and store sensitive information.

# Database credentials management
resource "scaleway_secret" "db_credentials" {
  name        = "db-credentials"
  description = "Information needed to access the ${scaleway_rdb_instance.postgre_server.name} database."
  tags        = ["postgresql"]

  type        = "database_credentials"
}

resource "scaleway_secret_version" "db_secret_data" {
  description = "v1"
  secret_id   = scaleway_secret.db_credentials.id
  data        = jsonencode({
    engine = "postgres"
    username = scaleway_rdb_user.db_admin.name
    password = random_password.db_password.result
    host = scaleway_rdb_instance.postgre_server.load_balancer[0].hostname
    dbname = scaleway_rdb_instance.postgre_server.name
    port = tostring(scaleway_rdb_instance.postgre_server.load_balancer[0].port)
  })
}

# NATS server credentials management
resource "scaleway_secret" "nats_credentials" {
  name        = "nats-credentials"
  description = "Information needed to access the NATS server."
  tags        = ["nats"]

  type        = "certificate"
}

resource "scaleway_secret_version" "nats_secret_data" {
  description = "v1"
  secret_id   = scaleway_secret.nats_credentials.id
  data        = scaleway_mnq_nats_credentials.nats_creds.file
}