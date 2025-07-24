output "kubernetes_cluster_id" {
  value = module.kubernetes_module.cluster_id
  description = "The ID of the Kubernetes cluster."
}