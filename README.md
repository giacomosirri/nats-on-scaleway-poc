# Motivation
The goal of this project is to develop a distributed application that meets simplified but realistic vehicle telemetry collection needs by using Scaleway services.

Scaleway is a French cloud provider that is often cited as [one of the major players in Europe's Sovereign Cloud market](https://gartsolutions.com/digital-sovereignty-of-europe-choosing-the-eu-cloud-provider/#Top_European_Cloud_Providers_Supporting_Digital_Sovereignty). Its relevance and market share will most likely grow in the future, as the demand for digital sovereignty in Europe continues to rise.

The scenario considered here and its relative solution were designed to highlight some interesting and unique services of Scaleway, such as the possibility to host a NATS server.

Ultimately, the idea is to build a fully cloud-native solution, showing how a modern approach to software development in the cloud can bring scalable, reliable and efficient systems to life.   

# Scenario
A car manufacturer wants to equip its new vehicle fleet with IoT sensors that calculate the position (GPS), speed, state of charge, and torque of vehicles in real-time. The sensors turn on as soon as the vehicle engine starts up, and they turn off when the vehicle gets shut down.

Each sensor works independently from the others, which means that the *sampling rate* (i.e., the number of times per second a signal is produced) can vary significantly between the sensors. For example, a sensor may detect 30 new data points per second, while another only 5 per second.

The telemetry information detected by the sensors must be gathered into a centralized data storage solution, to allow for real-time visualization and analysis of vehicle status. In particular, the software must allow for time-series analysis on specific vehicles, as well as for aggregation of data coming from different vehicles.

There are some hard constraints that the solution must consider:
- Sensors have small amounts of CPU and memory.
- Vehicle-to-cloud communication must be secure and resilient.
- Data manipulation, storage and visualization must happen in the cloud, all in a single European sovereign cloud provider.
- The protocol used to send data to the cloud must be lightweight, reliable, and fast.
- The solution must be scalable, having to potentially collect data from thousands of vehicles at the same time.
- The solution must use as few cloud resources as possible, in order to minimize cloud footprint and costs.

# Solution

## Infrastructure resources
First of all, we need a messaging system to gather and centralize data coming from the sensors.

For this task we can use [NATS](https://github.com/nats-io) (Neural Autonomic Transport System), a cloud-native, open-source messaging system designed around performance, security and ease of use. NATS has been part of the [CNCF landscape](https://landscape.cncf.io/) as an incubating project since 2018.

NATS implements the *publish-subscribe* pattern, in which the **publisher** sends a message on a communication channel (in NATS it is called **Subject**) the **subscriber** can listen (or subscribe) to. Scaleway provides NATS accounts (i.e., servers) out of the box.

Then we also need a computing platform where to run these subscriber workloads.

Cloud-native software is about building containers and running them on Kubernetes. Scaleway provides managed Kubernetes clusters under the name of Kubernetes Kapsule. When creating a Kubernetes Kapsule cluster, you can choose the node type for your node pool, and set up nodes autoscaling, autohealing and isolation.

Since we want to model a scenario where NATS clients are installed in vehicles, it does not make sense to run these clients in the cloud, so we will simply run them locally with a [script](./app/src/launcher.sh). To ensure that they are small and efficient, clients are written in C using the official [NATS C client](https://github.com/nats-io/nats.c).

As for the database, there are several options available. An interesting one is Serverless SQL, a fully managed database service that automatically scales in storage and compute according to your workloads.

Compared to other more traditional solutions, such as Managed Database for PostgreSQL, for which you pay a fixed amount over time, with Serverless SQL you pay for what you actually use, and you can save more than 80% if you actively use the database only 2 hours per day.

We also need a data visualization service. One of the leading solutions in this field is [Grafana](https://grafana.com/grafana/). Grafana can integrate with several data sources, including PostgreSQL databases. By running Grafana as a container in the Kubernetes cluster, we achieve the goal of hosting the data visualization tool in the cloud without any additional cost.

Finally, we need to securely save credentials for the database and the NATS server. Scaleway provides Secret Manager, a managed and secure storage system for sensitive data such as passwords and API keys.

All in all, these are the main infrastructural resources we need to run this system:

### Client-side
- NATS client running locally

### Server-side
- Scaleway NATS account
- Scaleway Kubernetes Kapsule

### Data visualization
- Scaleway Serverless SQL PostgreSQL managed instance
- Grafana pod running in Kubernetes Kapsule

### Credentials management
- Scaleway Secret Manager

## Architecture diagram
![Architecture diagram](architecture-diagram.png)

## Explanation
For the use case at hand, we can assume that when a vehicle starts up, the ECU executes several NATS clients, one for each physical sensor. These clients publish messages to the NATS server, each on a separate hierarchical subject (e.g. vehicle.145.speed, where 145 is the id of the vehicle).

*Note: In this POC, the data produced by the NATS clients is completely random. For the sake of simplicity, the generated data points are floating point values in the [0,100] range.*

The NATS server is "observed" by a group of subscribers, all carrying out the same task: they read one incoming message at a time, and they write its payload to a dedicated store inside the NATS server. 

There is no subdivision of the subscribers into separate specialized groups. Instead, every subscriber can read every message, regardless of the topic the message belongs to. This architectural decision automatically ensures a fair and efficient use of the available compute resources, even in case of wildly different sensor sampling rates.

Of course, saving data to the NATS internal storage is not enough to achieve our end goals. There needs to be another service that aggregates data across the sensors at a common point in time, and writes a consistent, time-stamped record to the database. This is exactly what the aggregator does.

When records are written to the PostgreSQL database, the user can access and visualize them on Grafana by connecting via browser to the Grafana service endpoint.

### Technical details

#### NATS and Queue Groups
NATS provides several interesting features. Some of them have been used here to achieve the target scenario. In this section I will explain the solution from a technical point of view, with a particular focus on these NATS concepts. 

A very important out-of-the-box feature of NATS are the Queue Groups. If multiple subscribers are assigned to the same Queue Group for a subject, each time a message is published on that subject, only one randomly selected subscriber receives it.

This makes it possible to have multiple subscribers listening in parallel to the same subject, each consuming a message that no other subscriber will ever read. This is crucial for us, because it means that the number of subscribers can simply scale in or out according to the number of active vehicles (even though, to make things simpler, the number of subscriber replicas is set to 5 for this POC).

However, Queue Groups alone don't prevent the risk of losing messages when the cluster where the subscribers run is down. The publish-subscribe pattern doesn't contemplate storing the messages, so when a message is sent, there needs to be at least one subscriber active on that subject, otherwise the message will be lost.

#### Subscribers implementation with JetStream and Key/Value Store
Luckily, NATS can be "enhanced" by using [JetStream](https://docs.nats.io/nats-concepts/jetstream), a persistence engine that enables messages to be stored and replayed at a later time. This crucially means that even in case there is no active subscriber when a message is sent, the message will not be lost.

JetStream also offers an *exactly once* quality of service. In other words, JetStream ensures that subscribers receive *all* the messages produced by the publishers without duplicates. All in all, these JetStream features make the system extremely resilient, stable, and scalable.

However, what really makes JetStream a must for this solution is the Key/Value Store, a feature that allows JetStream clients to create *buckets* (i.e. associative arrays, aka dictionaries), where they can store data in the form of key-value entries, thus replicating a functionality commonly found in proper key-value databases such as Redis.

I implemented the persistence of sensor messages using only one bucket, so that the aggregator workload can read data produced by every sensor and vehicle from this unique data source, thus respecting the [Single Source of Truth](https://en.wikipedia.org/wiki/Single_source_of_truth) principle.

Thanks to a nice feature of the Python NATS library, the bucket is automatically created when the "first" subscriber requests a *pointer* to the bucket. When the other subscribers call the same method later on, JetStream recognizes that a bucket with that name already exists, so it doesn't create a new one and only returns a pointer to the existing one.

This comes very handy, because it implies that the subscribers can all run the same Python coroutine, so there is no need to implement a subscriber (or another workload) with the specific purpose of creating the bucket.

Operatively speaking, a subscriber is a member of the queue group, and as such it continuously waits for a message to come. As soon as it receives a message, the subscriber writes that piece of telemetry data to the bucket, mapping the value to a string key that contains information about the sensor and the vehicle the message was produced by. That is basically all that subscribers do, nothing more than that.

#### Aggregator implementation

The aggregator workload reads data from the bucket every *x* seconds, and for each vehicle it creates a record that contains one value for each sensor, then it persists it to the PostgreSQL database. If a sensor doesn't send data, then the aggregator simply puts NULL in place of the value.

Now it is interesting to think about how the Key/Value Store saves data. Let's consider this scenario: one of the vehicle's sensors produces messages every 2 seconds, while the aggregator is configured to read from the bucket once every minute. What could happen is that the aggregator finds `60/2 = 30` messages for that sensor, in case the entries get deleted from the bucket as soon as they are read, or maybe it finds all the entries ever stored.

Nevertheless, Key/Value Store operates differently. When a new key-value entry is written to the bucket, what happens is that the previous value associated to that key, if already present, gets overwritten. This might be an undesirable effect for scenarios where you want to keep track of the bucket's history, but it is perfect in this case.

As a matter of fact, the aggregator doesn't really need to know all the values the publishers sent over time, rather just the last one they sent before the process of reading data from the bucket begins. Of course, in a real-world scenario this is true only for small intervals between two reads (at most 2-3 seconds), since a vehicle can change its state really quickly, for example when accelerating. Interpolation might be used if the end goal is to derive continuous functions from discrete, timestamped measurements.

In this POC, the aggregator is configured to read at the turn of every new minute, which is probably not acceptable in reality, based on the explanation above. This parameter can also be changed to a lower value, but under a certain threshold the program *as-is* would not work anymore, because the process of reading from the bucket and writing to the database would not be finished in time to start a new step of this loop.

A workaround is to use multithreading in the aggregator core function, so that each thread autonomously and concurrently takes charge of a step. 

There are probably many other improvements that could be applied to tailor this solution to real-world use cases. Anyway, I hope this POC can be a good starting point to get familiar with Scaleway services and to understand how to take advantage of certain NATS peculiarities :).