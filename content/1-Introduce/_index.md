---
title : "Introduction"
date :  "`r Sys.Date()`" 
weight : 1 
chapter : false
pre : " <b> 1. </b> "
---
**What is Amazon EnventBridge**

- **Serverless event** bus service for AWS services
- Build **event-drive applications** at scale using events generated from your apps
- Use to connet your applications with data from a variety of sources, integrated SaaS applications
- AWS services to targets such as AWS lambda function

**- Amazon EventBridge Events**
An event indicates a change in an environment such as an AWS environment of a SaaS partnet service. Events are represented as JSON obj and they all have similar structure and the same top-level fields


![1](/FCJ2024-Mission2/images/eventbridge-content-filtering-1.png)

![2](/FCJ2024-Mission2/images/eventbridge.png)

**Benefits of Amazon EventBridge**

**- Build event-drive architecture:** 

With EventBridge, your target don't need to be awareof event sources because you can filter and publish directly to EventBridge. Improve developer agility as well as application resiliency with loosely coupled event-drive architectures.

**- Connect SaaS apps**

EventBridge ingest data supporte SaaS applications and routes it to AWS services and SaaS targets, SaaS apps to trigger workflow s for customer support, business operations

**- Write less custome code**

You can ingest, filter, transform and deliver events without writing custom code. The EventBridge schema registry stores a collection of easy-to-find event schemas

**- Reduce opertaional overhead**

There are no servers to provision, patch and management automatically based on the number of events ingested. Built-in distributed availability and fault-tolerance. Native event archive and replay capability


**EventBridge includes two ways to process events: event buses and pipes.**

- Event buses are routers that receive events and delivers them to zero or more targets. Event buses are well-suited for routing events from many sources to many targets, with optional transformation of events prior to delivery to a target.Rules associated with the event bus evaluate events as they arrive. Each rule checks whether an event matches the rule's pattern. If the event does match, EventBridge sends the event. You associate a rule with a specific event bus, so the rule only applies to events received by that event bus.

![pic](/FCJ2024-Mission2/images/eventbus.PNG)

- Pipes EventBridge Pipes is intended for point-to-point integrations; each pipe receives events from a single source for processing and delivery to a single target. Pipes also include support for advanced transformations and enrichment of events prior to delivery to a target.

![pic](/FCJ2024-Mission2/images/eventpipe.PNG)

Pipes and event buses are often used together. A common use case is to create a pipe with an event bus as its target; the pipe sends events to the event bus, which then sends those events on to multiple targets. For example, you could create a pipe with a DynamoDB stream for a source, and an event bus as the target. The pipe receives events from the DynamoDB stream and sends them to the event bus, which then sends them on to multiple targets according to the rules you've specified on the event bus.