# Output database connection information so that it can be stored inside a vault/secret manager.
output "admin_username" {
  value = scaleway_rdb_user.db_admin.name
  sensitive = false
}

output "admin_password" {
  value = scaleway_rdb_user.db_admin.password
  sensitive = true
}

output "host" {
  value = scaleway_rdb_instance.postgre_server.load_balancer[0].hostname
  sensitive = false
}

output "name" {
  value = scaleway_rdb_instance.postgre_server.load_balancer[0].name
  sensitive = false
}

output "port" {
  value = tostring(scaleway_rdb_instance.postgre_server.load_balancer[0].port)
  sensitive = false
}
