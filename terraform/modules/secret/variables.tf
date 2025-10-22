variable "db_connection" {
  type = object({
    engine   = string
    username = string
    password = string
    dbname   = string
    host     = string
    port     = string
  })
  description = "Database connection details."
}

variable "nats_credentials_file" {
  type        = string
  description = "The content of the NATS credentials file."
}