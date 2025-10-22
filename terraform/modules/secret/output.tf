output "db_connection_secret_id" {
  // ID of the secret containing the database connection string.
  value = scaleway_secret.db_connection.id
}