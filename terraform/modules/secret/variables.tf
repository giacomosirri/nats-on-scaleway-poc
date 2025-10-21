variable "db_connection" {
  type = string
  description = "Database connection string."
}

variable "nats_credentials_file" {
  type        = string
  description = "The content of the NATS credentials file."
}