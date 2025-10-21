output "kubernetes_cluster_id" {
  value = module.kubernetes_module.cluster_id
  description = "The ID of the Kubernetes cluster."
}

output "db_connection_secret_id" {
  value = module.secret_module.db_connection_secret_id
  description = "The ID of the Secret containing the database connection string."
}