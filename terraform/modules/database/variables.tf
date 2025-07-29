variable "database_server_name" {
  type        = string
  description = "The name of the PostgreSQL server instance."
}

variable "database_name" {
  type        = string
  description = "The name of the PostgreSQL database instance."
}

variable "vpc_private_network_id" {
  type        = string
  description = "The ID of the VPC private network to use for the database instance."
}