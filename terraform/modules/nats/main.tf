resource "scaleway_mnq_nats_account" "nats_acc" {
  name = "${var.nats_account_name}"
}

resource "scaleway_mnq_nats_credentials" "nats_creds" {
  account_id = scaleway_mnq_nats_account.nats_acc.id
}
