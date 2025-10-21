data "scaleway_account_project" "my_account" {
  name = "giacomo-sirri"
}

resource "scaleway_iam_application" "app" {
  name = "ServerlessDBApp"
}

resource "scaleway_iam_policy" "db_access" {
  name           = "DBAccessPolicy"
  description    = "Gives app access to serverless database in project"
  application_id = scaleway_iam_application.app.id
  rule {
    project_ids          = [data.scaleway_account_project.my_account.id]
    permission_set_names = ["ServerlessSQLDatabaseReadWrite"]
  }
}

resource scaleway_iam_api_key "api_key" {
  application_id = scaleway_iam_application.app.id
}

resource scaleway_sdb_sql_database "database" {
  name    = var.database_name
  min_cpu = 0
  max_cpu = 4
}