import sys
import asyncio
import nats

async def message_read(msg):
    print(f"Received a message from vehicle: {msg.subject.split('.')[1]}")
    print(f"Status: {"ON" if msg.data.decode() else "OFF"}")
    
async def subscribe(topic):
    nc = await nats.connect("nats://nats.mnq.fr-par.scaleway.com:4222", user_credentials="./app/secrets/nats-credentials.txt")
    sub = await nc.subscribe(f"vehicle.*.{topic}", cb=message_read)

if __name__ == "__main__":
    topic = sys.argv[1]
    asyncio.run(subscribe(topic))
    while True:
        pass  # Keep the script running to listen for messages