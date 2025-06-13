resource "scaleway_rdb_instance" "postgre_server" {
  name           = "${var.database_server_name}"
  tags           = ["postgresql"]
  node_type      = "DB-DEV-S"
  engine         = "PostgreSQL-15"
  is_ha_cluster  = false
  disable_backup = true
}

resource "random_password" "db_password" {
  length  = 16
  special = true
  min_numeric = 1
  min_upper = 1
}

resource "scaleway_rdb_user" "db_admin" {
  instance_id = scaleway_rdb_instance.postgre_server.id
  name        = "admin"
  password    = random_password.db_password.result
  is_admin    = true
}

resource "scaleway_rdb_database" "sensor_data_db" {
  instance_id    = scaleway_rdb_instance.postgre_server.id
  name           = "${var.database_name}"
}