import os
from scaleway import Client
from scaleway.secret.v1beta1.api import SecretV1Beta1API
import base64

def get_nats_credentials():
    scw_client = Client(
        access_key=os.environ["SCW_ACCESS_KEY"],
        secret_key=os.environ["SCW_SECRET_KEY"],
        default_project_id="d43489e8-6103-4cc8-823b-7235300e81ec",
        default_region="fr-par",
        default_zone="fr-par-1"
    )
    ssm_api = SecretV1Beta1API(scw_client)
    base64_nats_credentials = ssm_api.access_secret_version_by_path(secret_path="/",
                                                                    secret_name="nats-credentials",
                                                                    revision="latest")
    nats_credentials = base64.b64decode(base64_nats_credentials.data).decode("utf-8")
    return nats_credentials

# This implementation has the advantage of incapsulating all the logic
# of writing NATS credentials to a file into a single function.
# Callers don't need to worry about the file path or directory structure.
def write_nats_credentials_to_file(nats_credentials):
    file_path = "/".join([os.getcwd(), "secrets/nats-credentials.creds"])

    # Create the directory if it does not exist.
    if not os.path.exists(os.path.dirname(file_path)):
        try:
            os.makedirs(os.path.dirname(file_path))
        except OSError as e:
            return None
        
    try:
        # Write the NATS credentials to the file and return the file path.
        with open(file_path, "w") as f:
            f.write(nats_credentials)
        return file_path
    except IOError as e:
        return None
