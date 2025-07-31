resource "scaleway_rdb_instance" "postgre_server" {
  name           = "${var.database_server_name}"
  tags           = ["postgresql"]
  node_type      = "DB-DEV-S"
  engine         = "PostgreSQL-15"

  is_ha_cluster  = false
  disable_backup = true

  private_network {
    pn_id  = "${var.vpc_private_network_id}"
    enable_ipam = true
  }
}

resource "random_password" "db_password" {
  length      = 16
  special     = true
  min_numeric = 1
  min_upper   = 1
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

resource "scaleway_rdb_privilege" "all_permissions" {
  instance_id   = scaleway_rdb_instance.postgre_server.id
  user_name     = scaleway_rdb_user.db_admin.name
  database_name = scaleway_rdb_database.sensor_data_db.name
  permission    = "all"
}