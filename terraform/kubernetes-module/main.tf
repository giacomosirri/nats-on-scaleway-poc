# Scaleway Kapsule multi-AZ VPC
resource "scaleway_vpc" "vpc_multi_az" {
  name = "vpc-multi-az"
  tags = ["multi-az"]
}

resource "scaleway_vpc_private_network" "pn_multi_az" {
  name   = "pn-multi-az"
  vpc_id = scaleway_vpc.vpc_multi_az.id
  tags   = ["multi-az"]
}

# Scaleway Kapsule cluster
resource "scaleway_k8s_cluster" "kapsule_multi_az" {
  name                        = "${var.cluster_name}"
  tags                        = ["multi-az"]
  type                        = "kapsule"
  version                     = "1.32.3"
  cni                         = "cilium"
  
  delete_additional_resources = true
  
  autoscaler_config {
    scale_down_delay_after_add = "5m"
    scale_down_unneeded_time   = "5m"
  }

  private_network_id          = scaleway_vpc_private_network.pn_multi_az.id
}

# Scaleway Kapsule node pool
# A node pool is region-bounded and its machines are all of the same type.
resource "scaleway_k8s_pool" "pool_multi_az" {
  for_each = {
    "fr-par-1" = 1,
    "fr-par-2" = 2,
    "fr-par-3" = 3
  }

  name                   = "pool-${each.value}"
  zone                   = each.key
  tags                   = ["multi-az"]
  node_type              = "GP1-XS"

  cluster_id             = scaleway_k8s_cluster.kapsule_multi_az.id

  size                   = 1  // Initial size
  min_size               = 1
  max_size               = 3
  autoscaling            = true

  autohealing            = true
  container_runtime      = "containerd"
  root_volume_size_in_gb = 20
}