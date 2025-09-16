# Motivation
The objective of this project is to build a software that solves a simplified but reasonable real-world business scenario using Scaleway cloud services, with particular focus on its NATS and Kubernetes offerings. 

Scaleway is a French cloud provider that is often cited as [https://gartsolutions.com/digital-sovereignty-of-europe-choosing-the-eu-cloud-provider/#Top_European_Cloud_Providers_Supporting_Digital_Sovereignty](one of the major players in Europe's Sovereign Cloud market). Its relevance and market share will most likely grow in the future, as the demand for digital sovereignty in Europe continues to rise.

# Scenario
A car manufacturer wants to equip its upcoming vehicle fleet with sensors for position, speed, fuel and braking liquid temperature. The goal is to have a real-time, comprehensive solution for analysis and visualization of data collected from vehicles. The solution should allow the aggregation of data from multiple vehicles, as well as time-series analysis on single vehicles.

There are some constraints:

- sensors must be cheap and have little amounts of CPU and memory;
- vehicle-to-cloud communication must be secure and resilient;
- data manipulation, storage, analysis, and visualization must happen in the cloud, all in one single sovereign EU cloud provider;
- the messaging protocol used by the sensors must be lightweight, reliable, and fast;
- the solution must be scalable, potentially collecting data from hundreds of thousands of vehicles at the same time;
- the solution must use as few cloud resources as possible, in order to minimize cloud footprint and costs.
  
# Solution

## Minimum infrastructure resources

### Client-side
- NATS client

### Server-side
- NATS server
- Kubernetes cluster

### Data visualization
- PostgreSQL managed instance
- Grafana instance

## Architecture diagram
![Architecture diagram](architecture-diagram.png)

## Implementation details
All of the minimum resources presented above are offered by Scaleway as PaaS (managed) solutions.

Scaleway provides a NATS account (server) resource. [https://github.com/nats-io](NATS) (Neural Autonomic Transport System) is a cloud-native, open-source messaging system designed around performance, security and ease of use. It has been part of the [https://landscape.cncf.io/](CNCF landscape) as an incubating project since 2018.

NATS implements the *publish/subscribe* messaging pattern. In this scenario, we will assume that when a vehicle starts up, the ECU runs several NATS clients, one for each physical sensor. Every one of these clients publishes data to the NATS server on a separate subject. 

The NATS server is observed by many *subscribers*, all of which carry out the same task: they collect a specific signal sent by a sensor and then they write the data to a bucket managed by NATS.