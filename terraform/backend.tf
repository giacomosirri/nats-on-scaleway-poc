terraform {
  # No locking mechanism is yet supported. Therefore, using Scaleway object storage
  # as Terraform backend is not suitable when working in a team with a risk of 
  # simultaneous access to the same plan.
  backend "s3" {
    bucket                      = "terraform-state"
    key                         = "my_state.tfstate"
    region                      = "fr-par"
    endpoint                    = "https://s3.fr-par.scw.cloud"
    skip_credentials_validation = true
    skip_region_validation      = true
    skip_requesting_account_id  = true
  }
}