#!/bin/bash

FILE="secrets/scw-secret.txt"
while IFS= read -r line; do
    # Do not read empty lines or comments.
    [[ -z "$line" || "$line" =~ ^# ]] && continue
    export "$line"
done < "$FILE"

cleanup() {
    echo "Cleaning up..."
    for pid in "${pids[@]}"; do
        echo "Killing $pid"
        kill "$pid" 2>/dev/null
    done
    exit
}

pids=()

trap cleanup EXIT

# python3 src/subscribers/nats_aggregator.py & pids+=($!)
# python3 src/subscribers/nats_subscriber.py & pids+=($!)
# python3 src/subscribers/nats_subscriber.py & pids+=($!)
./bin/nats_client 123 "charge" 3 & pids+=($!)
./bin/nats_client 123 "torque" 5 & pids+=($!)
./bin/nats_client 123 "location_x" 2 & pids+=($!)
./bin/nats_client 123 "location_y" 2 & pids+=($!)
./bin/nats_client 567 "charge" 10 & pids+=($!)
./bin/nats_client 567 "speed" 4 & pids+=($!)

wait