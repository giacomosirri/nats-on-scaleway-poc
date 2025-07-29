locals {
  kubernetes_cluster_regional_id = scaleway_k8s_cluster.kapsule_multi_az.id
  kubernetes_cluster_id          = split("/", local.kubernetes_cluster_regional_id)[1]
}

output "cluster_id" {
  value       = local.kubernetes_cluster_id
  description = "The ID of the Kubernetes cluster."
}

output "cluster_vpc_private_network_id" {
  value       = scaleway_vpc_private_network.pn_multi_az.id
  description = "The ID of the private network used by the Kubernetes cluster."
}