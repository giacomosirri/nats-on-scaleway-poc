# Output database admin's password to store it inside a vault/secret manager.
output "admin_password" {
  value = scaleway_rdb_user.db_admin.password
  sensitive = true
}