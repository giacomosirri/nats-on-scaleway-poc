#!/bin/bash

python3 ./src/subscribers/nats_aggregator.py &
python3 ./src/subscribers/nats_subscriber.py &
python3 ./src/subscribers/nats_subscriber.py &
./bin/nats_client 123 "fuel" 3