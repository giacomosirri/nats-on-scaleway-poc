from datetime import datetime
import pytz

def get_current_localized_time():
    # Get the current time in the local timezone (Europe/Berlin)
    local_tz = pytz.timezone("Europe/Berlin")
    current_time = datetime.now(local_tz)
    return current_time.isoformat()

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