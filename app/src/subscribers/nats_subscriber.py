import asyncio
import nats
import sys
import os
from functools import partial
    
async def message_read(kv, msg):
    print(f"Message received on subject: {msg.subject}")
    topic = msg.subject.split('.')[2]
    if topic not in data.keys():
        print(f"Message is on an unexpected subject: {msg.subject}")
    else:
        value = float(msg.data.decode())
        print(f"{topic}: {value}")
        data[topic].append((float(msg.data.decode())))
        await kv.put(msg.subject, str(value).encode())

async def subscribe():
    # Connect to the NATS server.
    nc = await nats.connect("nats://nats.mnq.fr-par.scaleway.com:4222", user_credentials=FILE_PATH)
    if not nc.is_connected:
        print("Subscriber failed to connect to NATS server.")
        return False
    print("Subscriber connected to NATS server.")

    # Create JetStream context.
    js = nc.jetstream()

    # Create a Key/Value store.
    kv = await js.key_value('telemetry')

    # Subscribe to the topic.
    subject = await nc.subscribe(f"vehicle.*.*", queue="queue1", cb=partial(message_read, kv))
    print(f"Subscribed to topic: vehicle.*.*. Waiting for messages...")

    # Keep the subscriber running to listen for messages.
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("Shutting down...")
        entries: list = await kv.history("vehicle.123.fuel")
        for entry in entries:
            print(f"Key: {entry}")
        # Remove interest in subscription.
        await subject.unsubscribe()
        # Terminate connection to NATS.
        await nc.drain()
        return True

data = {
    "location": [],
    "fuel": [],
    "speed": [],
    "brake_temp": []
}

FILE_PATH = "/".join([os.getcwd(), "secrets/nats-credentials.txt"])

res = asyncio.run(subscribe())
if not res:
    print("Something went wrong during the subscription process. Shutting down...")
    sys.exit(1)
else:
    print("Subscriber has been shut down successfully.")
    print(f"Data received: {data}", flush=True)
    sys.exit(0)