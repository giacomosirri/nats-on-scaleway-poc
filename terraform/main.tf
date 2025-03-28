provider "scaleway" {
  project_id      = "d43489e8-6103-4cc8-823b-7235300e81ec"
  organization_id = "daf36079-e52c-416c-9535-d06742e48acc"
  region          = "fr-par"
  zone  	        = "fr-par-1"
}

variable "project_name" {
  type        = string
  description = "You can set meaningful names for Scaleway resources by setting this variable."
  default     = "test-project"
}

resource "scaleway_mnq_nats_account" "main" {
  name        = "nats-${var.project_name}"
}

resource "scaleway_instance_ip" "public_ip" {}

resource "scaleway_instance_server" "web" {
  name        = "vm-${var.project_name}"
  type        = "COPARM1-2C-8G"
  image       = "ubuntu_noble"
  ip_id       = scaleway_instance_ip.public_ip.id
}

resource "scaleway_rdb_instance" "main" {
  name           = "db-${var.project_name}"
  node_type      = "DB-DEV-S"
  engine         = "PostgreSQL-15"
  is_ha_cluster  = true
  disable_backup = true
  user_name      = "my_initial_user"
  password       = "thiZ_is_v&ry_s3cret"
}

resource "scaleway_rdb_database" "main" {
  instance_id    = scaleway_rdb_instance.main.id
  name           = "test-db-instance"
}