import asyncio
import nats
import sys
import os
from nats.js.errors import NoKeysError
from datetime import datetime
import pytz
from nats_credentials_handler import *
from utils import get_or_create_kv_bucket, get_current_localized_time
import psycopg

def get_sleeping_time():
    # Wait until the top of the next minute
    now = datetime.now(pytz.timezone("Europe/Berlin"))
    return 60 - now.second - now.microsecond / 1e6

async def main(nats_credentials_file, db_connection: psycopg.Connection):
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
                # Has the vehicle sent any new data?
                update = False
                values = {
                    "location_x": None,
                    "location_y": None,
                    "brake_temp": None,
                    "fuel": None,
                    "speed": None
                }

                # Filter to get the topics that this vehicle has sent data on, then loop through them.
                this_vehicle_keys = list(filter(lambda key: key.startswith(f"vehicle.{vehicle_id}."), keys))
                
                # The value of the variable 'key' here has format: vehicle.<vehicle_id>.<topic>.
                for key in this_vehicle_keys:
                    entry = await kv.get(key)
                    revision = entry.revision

                    if key not in seen_revisions or revision > seen_revisions[key]:
                        # The key is new or has been updated, which means the vehicle has sent new data.
                        update = True
                        topic = entry.key.split('.')[2]
                        if topic not in values.keys():
                            # The key is not valid, skip it.
                            print(f"[WARNING][{get_current_localized_time()}] {topic} is not a valid topic. Skipping...")
                            continue
                        else:
                            # Update the existing value for this topic.
                            values[topic] = entry.value.decode()
                        seen_revisions[key] = revision

                if update:
                    # Print the collected data.
                    print(f"[DEBUG][{clock_time}] Data aggregation for vehicle: {vehicle_id}")

                    # Save the collected data to the database.
                    with db_connection.cursor() as cur:
                        cur.execute(
                            "INSERT INTO vehicle_data.telemetry (vehicle_id, location_x, location_y, fuel, speed, brake_temp, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                            (
                                vehicle_id,
                                values["location_x"],
                                values["location_y"],
                                values["fuel"],
                                values["speed"],
                                values["brake_temp"],
                                clock_time
                            )
                        )
                        db_connection.commit()

    except KeyboardInterrupt:
        print(f"[INFO][{get_current_localized_time()}] Data aggregator received a shutdown signal. Shutting down...", flush=True)
        await nc.close()
    
if __name__ == "__main__":
    credentials_file_path = write_nats_credentials_to_file(get_nats_credentials())
    if credentials_file_path is None:
        print(f"[ERROR][{get_current_localized_time()}] Data aggregator failed to write NATS credentials to file. Shutting down...", flush=True)
        sys.exit(1)
    else:
        print(f"[INFO][{get_current_localized_time()}] Data aggregator saved NATS credentials to file.")
        # Connect to the PostgreSQL database.
        connection = psycopg.connect(
            dbname=os.getenv("PGDATABASE"),
            user=os.getenv("PGUSER"),
            password=os.getenv("PGPASSWORD"),
            host=os.getenv("PGHOST"),
            port=os.getenv("PGPORT", "5432")  # Default PostgreSQL port
        )
        with connection:
            print(f"[INFO][{get_current_localized_time()}] Data aggregator connected to the database.")
            # Run the main function.
            asyncio.run(main(credentials_file_path, db_connection=connection))
