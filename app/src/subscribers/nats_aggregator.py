import asyncio
import nats
from nats.js.errors import NoKeysError
from datetime import datetime
import pytz
import os
import sys
from scaleway import Client
from scaleway.secret.v1beta1.api import SecretV1Beta1API
import base64

# Dictionary to store last seen revisions
seen_revisions = {}

FILE_PATH = "/".join([os.getcwd(), "secrets/nats-credentials.txt"])
if not os.path.exists(os.path.dirname(FILE_PATH)):
    try:
        os.makedirs(os.path.dirname(FILE_PATH))
    except OSError as e:
        print(f"Failed to create directory for NATS credentials: {e}")
        sys.exit(1)

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

try:
    with open(FILE_PATH, "w") as f:
        f.write(nats_credentials)
    print("NATS credentials have been written to disk successfully.")
except IOError as e:
    print(f"Failed to write NATS credentials to file: {e}")
    sys.exit(1)

async def main():
    nc = await nats.connect("nats://nats.mnq.fr-par.scaleway.com:4222", user_credentials=FILE_PATH)

    js = nc.jetstream()

    # Create or bind to existing KV bucket
    try:
        kv = await js.create_key_value(bucket="telemetry")
    except:
        kv = await js.key_value("telemetry")

    print("Connected to KV bucket: telemetry")

    while True:
        # Wait until the top of the next minute
        now = datetime.now(pytz.timezone("Europe/Berlin"))
        sleep_seconds = 60 - now.second - now.microsecond / 1e6
        print(f"\n[{now.isoformat()}] Waiting for {sleep_seconds:.2f} seconds until the next minute tick...")
        await asyncio.sleep(sleep_seconds)

        print(f"\n[{now.isoformat()}] Minute tick")

        try:
            keys = await kv.keys()
        # For some reason, if the KV store is empty, it raises NoKeysError.
        except NoKeysError as e:
            keys = []
            print("No keys found in the KV store.")

        for key in keys:
            try:
                entry = await kv.get(key)
            except:
                continue  # key was deleted or expired

            rev = entry.revision
            if key not in seen_revisions or rev > seen_revisions[key]:
                # New or updated value
                value = entry.value.decode()
                print(f"{key} updated (rev {rev}): {value}")
                seen_revisions[key] = rev
            else:
                # Unchanged
                pass

asyncio.run(main())
