import asyncio
import nats

async def publish():
    nc = await nats.connect("nats://nats.mnq.fr-par.scaleway.com:4222", user_credentials="client1-creds.creds")
    
    for i in range(10):  # Sending 10 messages as an example
        message = f"Vehicle speed: {20 + i} km/h"
        await nc.publish("vehicle.speed", message.encode())
        print(f"Published: {message}")
        await asyncio.sleep(1)  # Simulate a delay between messages

    await nc.close()

if __name__ == "__main__":
    asyncio.run(publish())