---
title: "Api gateway"
date: "`r Sys.Date()`"
weight: 5
chapter: false
pre: " <b> d. </b> "
---

[api reference](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_apigateway-readme.html)

Defining API that includes the following HTTP endpoints:

- GET /order
- GET /order/{userName}?date=timestamp

Using AWS Lambda as the backend integration (basket/index.js). The full stack will be in the next section for better understanding.

```
 const apigw3 = new LambdaRestApi(this, "orderApi", {
        proxy: false,
        restApiName: "Order Service",
        handler: ofunction,
      });
      const order = apigw3.root.addResource("order");
      order.addMethod("GET");
      const singleorder = order.addResource("{userName}");
      singleorder.addMethod("GET");
```
