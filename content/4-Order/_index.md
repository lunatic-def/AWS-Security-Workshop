---
title : "Order service"
date : "`r Sys.Date()`"
weight : 4
chapter : false
pre : " <b> 4. </b> "
---

**Preview of AWS SQS**
- AWS SQS (simple queue service) is a fully managed message queues for microservices distributed systems, and serverless applications.
- Enables you to decouple and scale microservices, distributed systems, and serverless applications.
- Eliminates the complexity and overhead associated with managing operating message-oriented middleware.
- Send, store and receive messages between software components at any volume.
- Two types and decpuple distributed software systems and components.
    - Standard queues offer maximum throughput, best-effort ordering, and at-least-once delivery.
    - FIFO queue are designed to gurantee that messages are processed exactly once, in the exact order that they are sent 
- Provides a generic web service API that you can access using any programming language that hte AWS SDK support. 


**In this section we will continue developing checkout event with basket and order service using EvenBridge and SQS services**
![topo](/FCJ2024-Mission2/images/4-order/topo.png)

=> Create an event resilience architecture for case like when order service when down, the event won disapper. Instead it will wait in the sqs queue 

=> SUMMARY: Basket service will publish event to eventbridge if event satified the eventbridge rule -> go to SQS queue to subscribe to Order service