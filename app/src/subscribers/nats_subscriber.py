import asyncio
import nats
import sys
import os
from functools import partial
from nats_credentials_handler import get_current_localized_time, write_nats_credentials_to_file, get_nats_credentials

valid_keys = ["location", "fuel", "speed", "brake_temp"]

async def message_read(kv, msg):
    topic = msg.subject.split('.')[2]
    if topic not in valid_keys:
        print(f"[WARNING][{get_current_localized_time()}] Data consumer received a message on an unexpected subject: {msg.subject}. Skipping...")
    else:
        value = float(msg.data.decode())
        print(f"[DEBUG][{get_current_localized_time()}] New message received by data consumer ({msg.subject}: {value}). Saving it in the KeyValue store...")
        await kv.put(msg.subject, str(value).encode())

async def subscribe(nats_credentials_file):
    # Connect to the NATS server.
    nc = await nats.connect("nats://nats.mnq.fr-par.scaleway.com:4222", user_credentials=nats_credentials_file)
    if not nc.is_connected:
        print(f"[ERROR][{get_current_localized_time()}] Data consumer failed to connect to NATS server.")
        return False
    print(f"[INFO][{get_current_localized_time()}] Subscriber connected to NATS server.")

    # Create JetStream context.
    js = nc.jetstream()

    # Create a Key/Value store.
    kv = await js.key_value('telemetry')

    # Subscribe to the topic.
    topic = "vehicle.*.*"
    subject = await nc.subscribe(topic, queue="queue1", cb=partial(message_read, kv))
    print(f"[INFO][{get_current_localized_time()}] Data consumer subscribed to topic: {topic}.")

    # Keep the subscriber running to listen for messages.
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        print(f"[INFO][{get_current_localized_time()}] Data consumer received a shutdown signal. Shutting down...", flush=True)
        # Remove interest in subscription.
        await subject.unsubscribe()
        # Terminate connection to NATS.
        await nc.drain()

if __name__ == "__main__":
    credentials_file_path = write_nats_credentials_to_file(get_nats_credentials())
    if credentials_file_path is None:
        print(f"[ERROR][{get_current_localized_time()}] Data consumer failed to write NATS credentials to file. Shutting down...", flush=True)
        sys.exit(1)
    else:
        print(f"[INFO][{get_current_localized_time()}] Data consumer saved NATS credentials to file: {credentials_file_path}.")
        res = asyncio.run(subscribe(credentials_file_path))