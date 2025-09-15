# Motivation
The objective of this project is to build a software that solves a simplified but reasonable real-world business scenario using Scaleway cloud services, with particular focus on its NATS and Kubernetes offerings. 

Scaleway is a French cloud provider that is often cited as one of the major players in Europe's Sovereign Cloud market. Its relevance and market share will most likely grow in the future, as the demand for digital sovereignty in Europe continues to rise.

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
![Architecture diagram](architecture-diagram.png)

## Explanation
Scaleway provides all the necessary infrastructure resources to build a scalable cloud solution that meets every requirement of this scenario.

Scaleway provides a NATS account (*broker*) resource. NATS (Neural Autonomic Transport System) is a cloud-native, CNCF-incubating open-source messaging system designed for high-throughput and low-latency messaging, making it ideal for this use case.

NATS implements the *publish/subscribe* messaging pattern. In this scenario, vehicle sensors function as publishers, each publishing to a specific *subject*.

We can imagine that when a vehicle starts up, the ECU operating system runs several NATS clients, one for each sensor. Every client publishes data to the NATS server on a separate subject.

The NATS server is observed by many *subscribers*, all of which carry out the same task: they collect a specific signal sent by a vehicle and then they transmit it to the a bucket managed by NATS.