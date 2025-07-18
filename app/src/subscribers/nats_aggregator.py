import asyncio
import nats
import sys
from nats.js.errors import NoKeysError
from datetime import datetime
import pytz
from nats_credentials_handler import *
from utils import get_or_create_kv_bucket, get_current_localized_time

def get_sleeping_time():
    # Wait until the top of the next minute
    now = datetime.now(pytz.timezone("Europe/Berlin"))
    return 60 - now.second - now.microsecond / 1e6

async def main(nats_credentials_file):
    nc = await nats.connect("nats://nats.mnq.fr-par.scaleway.com:4222",
                            user_credentials=nats_credentials_file)
    js = nc.jetstream()

    kv = await get_or_create_kv_bucket(js, "telemetry")
    if kv is None:
        print(f"[ERROR][{get_current_localized_time()}] Data aggregator failed to connect to KV bucket:{kv._name}. Aborting...")
        return 1
    else:
        print(f"[INFO][{get_current_localized_time()}] Data aggregator is connected to KV bucket: {kv._name}.")
    
    try:
        while True:
            # Wait until the next minute starts.
            await asyncio.sleep(get_sleeping_time())
            clock_time = get_current_localized_time()
            print(f"[INFO][{clock_time}] Data aggregator starts aggregating data.")

            try:
                keys = await kv.keys()
            # For some reason, if the KeyValue store is empty, it raises NoKeysError.
            except NoKeysError as e:
                keys = []
                print(f"[WARNING][{get_current_localized_time()}] Data aggregator found no keys in the KV store.")

            vehicle_ids = set(map(lambda key: key.split('.')[1], keys))  # Extract the vehicle ids from the key
            
            seen_revisions = {}

            for vehicle_id in vehicle_ids:
                this_vehicle_keys = list(filter(lambda key: key.startswith(f"vehicle.{vehicle_id}."), keys))
                if len(this_vehicle_keys) == 0:
                    continue
                values = {
                    "location": None,
                    "fuel": None,
                    "speed": None,
                    "brake_temp": None
                }

                for key in this_vehicle_keys:
                    entry = await kv.get(key)

                    rev = entry.revision
                    if key not in seen_revisions or rev > seen_revisions[key]:
                        # The key is new or has been updated, which means the vehicle has sent new data.
                        topic = entry.key.split('.')[2]
                        if topic not in values.keys():
                            # The key is not valid.
                            print(f"[WARNING][{get_current_localized_time()}] {topic} is not a valid topic. Skipping...")
                        else:
                            # Update the existing key
                            values[topic] = entry.value.decode()
                        seen_revisions[key] = rev
                    else:
                        # The key has not been updated since the last time it was checked,
                        # which means the vehicle has not sent new data, possibly because it is now off.
                        pass
                # Print the collected data.
                print(f"[DEBUG][{clock_time}] Data aggregation for vehicle: {vehicle_id}")
                for (topic, value) in values.items():
                    print(f"{topic}: {value if value is not None else 'No data'}")
    except KeyboardInterrupt:
        print(f"[INFO][{get_current_localized_time()}] Data aggregator received a shutdown signal. Shutting down...", flush=True)
        await nc.close()
    
if __name__ == "__main__":
    credentials_file_path = write_nats_credentials_to_file(get_nats_credentials())
    if credentials_file_path is None:
        print(f"[ERROR][{get_current_localized_time()}] Data consumer failed to write NATS credentials to file. Shutting down...", flush=True)
        sys.exit(1)
    else:
        print(f"[INFO][{get_current_localized_time()}] Data consumer saved NATS credentials to file: {credentials_file_path}.")
        asyncio.run(main(credentials_file_path))
