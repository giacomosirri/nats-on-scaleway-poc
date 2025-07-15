import asyncio
import base64
import nats
import os
import sys
from scaleway import Client
from scaleway.secret.v1beta1.api import SecretV1Beta1API

async def message_read(msg):
    print(f"Message received on subject: {msg.subject}")
    topic = msg.subject.split('.')[2]
    if topic not in data.keys():
        print(f"Message is on an unexpected subject: {msg.subject}")
    else:
        value = float(msg.data.decode())
        print(f"{topic}: {value}")
        data[topic].append((float(msg.data.decode())))


async def subscribe():
    # Connect to the NATS server.
    nc = await nats.connect("nats://nats.mnq.fr-par.scaleway.com:4222", user_credentials=FILE_PATH)
    if not nc.is_connected:
        print("Subscriber failed to connect to NATS server.")
        return False
    print("Subscriber connected to NATS server.")

    # Subscribe to the topic.
    await nc.subscribe(f"vehicle.*.*", queue="queue1", cb=message_read)
    print(f"Subscribed to topic: vehicle.*.*. Waiting for messages...")

    # Keep the subscriber running to listen for messages.
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("Shutting down...")
        return True


FILE_PATH = "/".join([os.getcwd(), "secrets/nats-credentials.txt"])
if not os.path.exists(os.path.dirname(FILE_PATH)):
    try:
        os.makedirs(os.path.dirname(FILE_PATH))
    except OSError as e:
        print(f"Failed to create directory for NATS credentials: {e}")
        sys.exit(1)
        
data = {
    "location": [],
    "fuel": [],
    "speed": [],
    "brake_temp": []
}

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

res = asyncio.run(subscribe())
if not res:
    print("Something went wrong during the subscription process. Shutting down...")
    sys.exit(1)
else:
    print("Subscriber has been shut down successfully.")
    print(f"Data received: {data}", flush=True)
    sys.exit(0)