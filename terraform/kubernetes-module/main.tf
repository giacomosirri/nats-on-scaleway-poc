variable "cluster_name" {
  type        = string
  description = "The name of the Kubernetes Kapsule cluster."
  default     = "kube-cluster"
}

resource "scaleway_vpc_private_network" "pn" {}

resource "scaleway_k8s_cluster" "cluster" {
  name                        = "${var.cluster_name}"
  version                     = "1.29.1"
  cni                         = "cilium"
  private_network_id          = scaleway_vpc_private_network.pn.id
  delete_additional_resources = true
  autoscaler_config {
    scale_down_delay_after_add = "5m"
    scale_down_unneeded_time   = "5m"
  }
}

resource "scaleway_k8s_pool" "pool" {
  cluster_id  = scaleway_k8s_cluster.cluster.id
  name        = "kube-pool"
  node_type   = "DEV1-M"
  size        = 1  // Initial size
  min_size    = 1
  max_size    = 3
  autoscaling = true
}