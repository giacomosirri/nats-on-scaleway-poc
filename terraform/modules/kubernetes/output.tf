locals {
  kubernetes_cluster_regional_id = scaleway_k8s_cluster.kapsule_multi_az.id
  kubernetes_cluster_id          = split("/", local.kubernetes_cluster_regional_id)[1]
}

output "cluster_id" {
  value       = local.kubernetes_cluster_id
  description = "The ID of the Kubernetes cluster."
}