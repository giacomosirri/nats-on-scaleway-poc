# Output database connection information so that it can be stored inside a vault/secret manager.
output "admin_username" {
  value = scaleway_iam_application.app.id
  sensitive = true
}

output "admin_password" {
  value = scaleway_iam_api_key.api_key.secret_key
  sensitive = true
}

output "name" {
  value = scaleway_sdb_sql_database.database.name
  sensitive = false
}

locals {
  endpoint = split("/", split("://", scaleway_sdb_sql_database.database.endpoint)[1])[0]
  hostname_and_port = split(":", local.endpoint)
}

output "host" {
  value = local.hostname_and_port[0]
  sensitive = true
}

output "port" {
  value = local.hostname_and_port[1]
  sensitive = false
}