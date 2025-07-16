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

python3 ./src/subscribers/nats_aggregator.py & pids+=($!)
python3 ./src/subscribers/nats_subscriber.py & pids+=($!)
python3 ./src/subscribers/nats_subscriber.py & pids+=($!)
./bin/nats_client 123 "fuel" 3 & pids+=($!)

wait