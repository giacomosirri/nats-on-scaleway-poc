from threading import Thread
import asyncio
import nats
import random
import datetime

async def publish(id: str):
    nc = await nats.connect("nats://nats.mnq.fr-par.scaleway.com:4222", user_credentials="client1-creds.creds")
    
    for i in range(10):  # Sending 10 messages as an example
        message = random.uniform(5.0, 85.0)
        await nc.publish(f"vehicle.{id}.speed", str(message).encode())
        print(f"Vehicle {id} published at {datetime.datetime.now()}")
        await asyncio.sleep(random.randrange(1, 15))  # Simulate a delay between messages

    await nc.close()

def run_thread(id):
    asyncio.run(publish(id))

threads: list[Thread] = []
for i in range(5):
    thread = Thread(target=run_thread, args=[i])
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()