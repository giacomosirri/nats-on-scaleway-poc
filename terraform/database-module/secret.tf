# Create a Secret Manager instance and store sensitive database information.
# This makes it easy for clients to securely retrieve username and password,
# as well as the host name, the database name and the port for access.

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

resource "scaleway_secret_version" "secret_data" {
  description = "v1"
  secret_id   = scaleway_secret.db_credentials.id
  data        = jsonencode({
    engine = "postgres"
    username = scaleway_rdb_user.db_admin.name
    password = random_password.db_password.result
    host = scaleway_rdb_instance.postgre_server.load_balancer[0].hostname
    dbname = scaleway_rdb_instance.postgre_server.name
    port = string(scaleway_rdb_instance.postgre_server.load_balancer[0].port)
  })
}