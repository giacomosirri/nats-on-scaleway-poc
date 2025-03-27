provider "scaleway" {
  project_id      = "d43489e8-6103-4cc8-823b-7235300e81ec"
  organization_id = "daf36079-e52c-416c-9535-d06742e48acc"
  region          = "fr-par"
  zone  	        = "fr-par-1"
}

variable "project_name" {
  type = string
  description = "You can set meaningful names for Scaleway resources by setting this variable."
  default = "test-project"
}

resource "scaleway_mnq_nats_account" "main" {
  name = "nats-${var.project_name}"
}