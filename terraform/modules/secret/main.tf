# Create a Secret Manager instance and store sensitive information.

# Database connection information
resource "scaleway_secret" "db_connection" {
  name        = "db-connection"
  description = "Information needed to access the ${var.db_connection.dbname} database."
  tags        = ["postgresql"]

  type        = "database_credentials"
}

resource "scaleway_secret_version" "db_secret_data" {
  description = "v1"
  secret_id   = scaleway_secret.db_connection.id
  data        = jsonencode(var.db_connection)
}

# NATS server credentials management
resource "scaleway_secret" "nats_credentials" {
  name        = "nats-credentials"
  description = "Information needed to access the NATS server."
  tags        = ["nats"]

  type        = "opaque"
}

resource "scaleway_secret_version" "nats_secret_data" {
  description = "v1"
  secret_id   = scaleway_secret.nats_credentials.id
  data        = var.nats_credentials_file
}