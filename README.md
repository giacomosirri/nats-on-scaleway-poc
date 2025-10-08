# Motivation
The goal of this project is to create a software that solves a simplified but reasonable real-world business scenario using Scaleway cloud services, with particular focus on its NATS and Kubernetes offerings. 

Scaleway is a French cloud provider that is often cited as [one of the major players in Europe's Sovereign Cloud market](https://gartsolutions.com/digital-sovereignty-of-europe-choosing-the-eu-cloud-provider/#Top_European_Cloud_Providers_Supporting_Digital_Sovereignty). Its relevance and market share will most likely grow in the future, as the demand for digital sovereignty in Europe continues to rise.

# Scenario
A car manufacturer wants to equip its new vehicle fleet with IoT sensors that calculate the position (GPS), speed, state of charge, and torque of vehicles in real-time. The sensors turn on as soon as the vehicle engine starts up, and they turn off when the vehicle gets shut down. Each sensor works independently from the others, which also means that the *sampling rate* (i.e., the number of times a signal is produced per second) can vary significantly. For example, a sensor might send 30 messages per second, while another sends only 5 messages per second.

The telemetry information detected by the sensors must be gathered into a centralized data storage solution, to allow for real-time analysis and visualization of vehicle status. The software must allow time-series analysis on specific vehicles, as well as aggregation of data coming from different vehicles.

There are some constraints:

- sensors have small amounts of CPU and memory, so the software must use resources efficiently;
- vehicle-to-cloud communication must be secure and resilient;
- data manipulation, storage and visualization must happen in the cloud, all in one single European sovereign cloud provider;
- the messaging protocol used to receive data from the sensors must be lightweight, reliable, and fast;
- the solution must be scalable, having to potentially collect data from thousands of vehicles at the same time;
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

### High-level explanation
The minimum resources presented above are all offered by Scaleway as PaaS (managed) services. The additional resources needed (e.g. Secret Manager) are also provided by Scaleway, which means that the constraint on the cloud provider can be respected.

Scaleway provides NATS accounts (aka servers). [NATS](https://github.com/nats-io) (Neural Autonomic Transport System) is a cloud-native, open-source messaging system designed around performance, security and ease of use. It has been part of the [CNCF landscape](https://landscape.cncf.io/) as an incubating project since 2018.

NATS implements the *publish-subscribe* pattern, in which the **publisher** sends a message on a communication channel (in NATS it is called **Subject**) the **subscriber** can listen (or subscribe) to.

For the use case at hand, we can assume that when a vehicle starts up, the ECU executes several NATS clients, one for each physical sensor. These clients publish messages to the NATS server, each on a separate hierarchical subject (e.g. vehicle.145.speed, where 145 is the id of the vehicle).

The NATS server is "observed" by a group of subscribers, all carrying out the same task: they read one incoming message at a time, and they write its payload to a dedicated store inside the NATS server. There is no subdivision of the subscribers into separate specialied groups. Instead, every subscriber can read every message, regardless of the topic the message belongs to. This architectural decision automatically ensures a fair and efficient use of the available compute resources, even in case of wildly different sensor sampling rates.

Of course, saving data to the NATS internal storage is not enough to achieve our end goals. There needs to be another service that aggregates data across the sensors at a common point in time, and writes a consistent, time-stamped record to a database. This is exactly what the aggregator does. Once a record is written to the PostgreSQL database, the user can visualize it in the Grafana instance, which is configured with the database as a data source.

### Technical details
