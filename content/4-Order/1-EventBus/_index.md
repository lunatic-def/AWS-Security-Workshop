---
title : "EventBus"
date : "`r Sys.Date()`"
weight : 1
chapter : false
pre : " <b> a. </b> "
---

![topo](/FCJ2024-Mission2/images/4-order/topo2.png)

+ [Api reference](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_events.EventBus.html)
```
        //create eventbus
        const bus = new EventBus(this, 'EventBus', {
            eventBusName: 'EventBus'
        });
        //create rule
        const CheckoutRule = new Rule(this, "CheckoutRule", {
          ruleName: "CheckoutBasketRule",
          eventBus: bus,
          enabled: true,
          description: "rule for when checkout basket",
          eventPattern: {
            source: ["com.swn.basket.checkoutbasket"],
            detailType: ["CheckoutBasket"],
          }
        });

        //add target to rule
        CheckoutRule.addTarget(new SqsQueue(*Subscriber*));
        // grant permission to function to create event to bus
        bus.grantPutEventsTo(*Publisher*);
```