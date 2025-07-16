import asyncio
import nats
import sys
import os
from functools import partial
from nats_credentials_handler import get_current_localized_time, write_nats_credentials_to_file, get_nats_credentials

valid_keys = [
    "location"
    "fuel"
    "speed"
    "brake_temp"
]

async def message_read(kv, msg):
    topic = msg.subject.split('.')[2]
    if topic not in valid_keys:
        print(f"[WARNING][{get_current_localized_time()}] Data consumer received a message on an unexpected subject: {msg.subject}. Skipping...")
    else:
        value = float(msg.data.decode())
        print(f"[WARNING][{get_current_localized_time()}] New value received by data consumer. Subject: {msg.subject}, value: {value}. Saving this data in the KeyValue store...")
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
        print(f"[INFO][{get_current_localized_time()}] Data consumer received a shutdown signal. Shutting down...")
        # Remove interest in subscription.
        await subject.unsubscribe()
        # Terminate connection to NATS.
        await nc.drain()

if __name__ == "__main__":
    credentials_file_path = write_nats_credentials_to_file(get_nats_credentials())
    res = asyncio.run(subscribe(credentials_file_path))