# Motivation
The idea is to implement a simplified real-world use case in the Scaleway cloud provider, with particular focus on its NATS and Kubernetes offerings.

# Scenario
A car manufacturer wants to equip its upcoming vehicle fleet with sensors for position, speed, fuel and braking liquid temperature. The goal is to have a real-time, comprehensive solution for analysis and visualization of data collected from vehicles. The solution should allow the aggregation of data from multiple vehicles, as well as time-series analysis on single vehicles.

There are some constraints:

- sensors must be cheap and have little amounts of CPU and memory;
- data manipulation, storage, analysis, and visualization must happen in the cloud, all in one single sovereign EU cloud provider;
- the messaging protocol used by the sensors must be lightweight, reliable, and fast;
- the solution must be scalable, potentially collecting data from hundreds of thousands of vehicles at the same time;
- the solution must use as few cloud resources as possible, in order to minimize cloud footprint and costs.
  
# Solution

## Resources required

### Client-side
- Lightweight NATS client written in C

### Server-side
- NATS server
- Kubernetes cluster
- Microservices running NATS *subscribers*

### Data visualization
- PostgreSQL managed instance
- Microservice running Grafana

## Architecture diagram
[Architecture diagram](architecture-diagram.png)

## Explanation
Scaleway provides all the necessary infrastructure resources to build a scalable cloud solution that meets every requirement of this scenario.

Scaleway provides a NATS account (*broker*) resource. NATS (Neural Autonomic Transport System) is a cloud-native, CNCF-incubating open-source messaging system designed for high-throughput and low-latency messaging, making it ideal for this use case.

NATS implements the *publish/subscribe* messaging pattern. In this scenario, vehicle sensors function as publishers, each publishing to a specific *subject*.

We can imagine that when a vehicle starts up, the ECU operating system runs several NATS clients, one for each sensor. Every client publishes data to the NATS server on a separate subject.

The NATS server is observed by many *subscribers*. One is the *Vehicle Discovery* pod in the Scaleway Kubernetes Kapsule cluster. This pods reads the *on* signals coming from the vehicles, and for each of them it sends a request to the Service in front of the NATS queue with the new vehicle's identifier.

This request triggers a binding process, that connects a vehicle and a pod. The binding is implicit in the way pull consumers work in a NATS queue, and lasts until the vehicle is turned off.

From this point on, all messages from a vehicle are processed by the same pod, because one single pod subscribes to all the subjects related to one specific vehicle. This binding facilitates efficient data aggregation.

For example, if one sensor publishes seven messages per minute while another publishes three, the assigned pod can interpolate data points to produce evenly-spaced timestamped records with data from all sensors.

When a pod completes processing a batch of records, it publishes them to the PostgreSQL database with TimescaleDB integration enabled. A Grafana service running on a Scaleway Compute instance queries this database to provide customizable views and charts.

The number of pods required depends on the number of active vehicles. To ensure reliability under high load without wasting resources during low demand, implementing pod autoscaling through KEDA (Kubernetes-based Event Driven Autoscaling) is required.

To prevent message loss when subscribers are overloaded, the NATS server can be configured with JetStream enabled, allowing messages to be stored and replayed later.