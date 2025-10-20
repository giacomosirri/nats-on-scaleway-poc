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
        latest_values = {}
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

            for vehicle_id in vehicle_ids:
                new_values = {}

                # Filter to get the topics that this vehicle has sent data on, then loop through them.
                this_vehicle_keys = list(filter(lambda key: key.startswith(f"vehicle.{vehicle_id}."), keys))
                
                # The value of the variable 'key' here has format: vehicle.<vehicle_id>.<topic>.
                for key in this_vehicle_keys:
                    # Get the new values for this key.
                    entry = await kv.get(key)
                    topic = key.split('.')[2]
                    new_values[topic] = entry.value.decode()

                # Compare the new values with the latest values one by one, 
                # and if there is one new key or at least one value is different, 
                # then write to the database.
                print(f"[DEBUG][{clock_time}] Data aggregator found these new values for vehicle {vehicle_id}: {new_values}.")
                old_values = latest_values.get(vehicle_id, {})
                print(f"[DEBUG][{clock_time}] Data aggregator found these latest values for vehicle {vehicle_id}: {old_values}.")
                update = False

                for topic, new_value in new_values.items(): 
                    if topic not in old_values or old_values[topic] != new_value:
                        old_values[topic] = new_value
                        update = True

                latest_values[vehicle_id] = new_values

                if update:
                    # Save the collected data to the database.
                    with db_connection.cursor() as cur:
                        cur.execute(
                            "INSERT INTO vehicle_data.telemetry (vehicle_id, location_x, location_y, charge, speed, torque, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                            (
                                vehicle_id,
                                new_values.get("location_x", None),
                                new_values.get("location_y", None),
                                new_values.get("charge", None),
                                new_values.get("speed", None),
                                new_values.get("torque", None),
                                clock_time
                            )
                        )
                        db_connection.commit()
                    print(f"[INFO][{clock_time}] Data aggregator saved new data for vehicle {vehicle_id} to the database.")

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
