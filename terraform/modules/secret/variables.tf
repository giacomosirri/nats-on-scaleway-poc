variable "db_connection" {
  type = object({
    engine   = string
    username = string
    password = string
    host     = string
    dbname   = string
    port     = string
  })
  description = "Database connection details."
}

variable "nats_credentials_file" {
  type        = string
  description = "The content of the NATS credentials file."
}