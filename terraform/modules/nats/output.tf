output "nats_creds" {
  value     = scaleway_mnq_nats_credentials.nats_creds.file
  sensitive = true
}
