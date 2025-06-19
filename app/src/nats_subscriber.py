import sys
import asyncio
import nats

data = {
    "location": [],
    "fuel": [],
    "speed": [],
    "brake_temp": []
}


async def message_read(msg):
    print(f"Message received at {msg.timestamp} on subject: {msg.subject}")
    topic = msg.subject.split('.')[2]
    if topic not in data.keys():
        print(f"Message is on an unexpected subject: {msg.subject}")
    else:
        value = float(msg.data.decode())
        print(f"{topic}: {value}")
        data[topic].append((float(msg.data.decode())))


async def subscribe(vehicle_id):
    # Connect to the NATS server.
    nc = await nats.connect("nats://nats.mnq.fr-par.scaleway.com:4222", user_credentials="../secrets/nats-credentials.txt")
    if not nc.is_connected:
        print("Subscriber failed to connect to NATS server.")
        return False
    print("Subscriber connected to NATS server.")

    # Subscribe to the topic.
    await nc.subscribe(f"vehicle.{vehicle_id}.*", cb=message_read)
    print(f"Subscribed to topic: vehicle.{vehicle_id}.*. Waiting for messages...")

    # Keep the subscriber running to listen for messages.
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("Shutting down...")
        return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python nats_subscriber.py <vehicle_id>")
        sys.exit(1)
    vehicle_id = sys.argv[1]
    res = asyncio.run(subscribe(vehicle_id))
    if not res:
        print("Something went wrong during the subscription process. Shutting down...")
        sys.exit(1)
    else:
        print("Subscriber has been shut down successfully.")
        print(f"Data received: {data}", flush=True)
        sys.exit(0)