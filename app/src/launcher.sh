#!/bin/bash

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

python3 src/subscribers/nats_aggregator.py & pids+=($!)
python3 src/subscribers/nats_subscriber.py & pids+=($!)
python3 src/subscribers/nats_subscriber.py & pids+=($!)
./bin/nats_client 123 "fuel" 3 & pids+=($!)
./bin/nats_client 123 "brake_temp" 5 & pids+=($!)
./bin/nats_client 123 "location_x" 2 & pids+=($!)
./bin/nats_client 123 "location_y" 2 & pids+=($!)
./bin/nats_client 567 "fuel" 10 & pids+=($!)
./bin/nats_client 567 "speed" 4 & pids+=($!)

wait