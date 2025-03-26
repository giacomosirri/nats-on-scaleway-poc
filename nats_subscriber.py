import asyncio
import nats

async def message_read(msg):
    print(f"Received a message on subject: {msg.subject}")
    print(f"Data: {msg.data.decode()}")
    
async def subscribe():
    nc = await nats.connect("nats://nats.mnq.fr-par.scaleway.com:4222", user_credentials="client1-creds.creds")
    
    sub = await nc.subscribe("vehicle.speed", cb=message_read)
    await asyncio.sleep(60)  # Remain alive for one minute
    await nc.close()

if __name__ == "__main__":
    asyncio.run(subscribe())