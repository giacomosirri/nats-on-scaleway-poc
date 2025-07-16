import asyncio
import nats
from nats.js.errors import NoKeysError
from datetime import datetime
import pytz
from nats_credentials_handler import *

async def get_or_create_kv_bucket(js, bucket_name):
    # Try to retrieve an existing KV bucket
    # If it does not exist, create a new one.
    try:
        kv = await js.key_value(bucket_name)
    except:
        try:
            kv = await js.create_key_value(bucket=bucket_name)
        except Exception as e:
            return None
    return kv

async def main():
    credentials_file_path = write_nats_credentials_to_file(get_nats_credentials())
    seen_revisions = {}
    nc = await nats.connect("nats://nats.mnq.fr-par.scaleway.com:4222",
                            user_credentials=credentials_file_path)
    js = nc.jetstream()
    
    kv = await get_or_create_kv_bucket(js, "telemetry")
    if kv is None:
        print(f"[ERROR][{get_current_localized_time()}] Failed to connect to or create KV bucket.")
        return 1
    
    while True:
        # Wait until the top of the next minute
        now = datetime.now(pytz.timezone("Europe/Berlin"))
        sleep_seconds = 60 - now.second - now.microsecond / 1e6
        print(f"\n[{now.isoformat()}] Waiting for {sleep_seconds:.2f} seconds until the next minute tick...")
        await asyncio.sleep(sleep_seconds)

        print(f"\n[{now.isoformat()}] Minute tick")

        try:
            keys = await kv.keys()
        # For some reason, if the KV store is empty, it raises NoKeysError.
        except NoKeysError as e:
            keys = []
            print("No keys found in the KV store.")

        for key in keys:
            try:
                entry = await kv.get(key)
            except:
                continue  # key was deleted or expired

            rev = entry.revision
            if key not in seen_revisions or rev > seen_revisions[key]:
                # New or updated value
                value = entry.value.decode()
                print(f"{key} updated (rev {rev}): {value}")
                seen_revisions[key] = rev
            else:
                # Unchanged
                pass

if __name__ == "__main__":
    asyncio.run(main())
