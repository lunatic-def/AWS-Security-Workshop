---
title: "Api gateway"
date: "`r Sys.Date()`"
weight: 4
chapter: false
pre: " <b> d. </b> "
---

[api reference](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_apigateway-readme.html)

Defining API that includes the following HTTP endpoints:

- GET /basket, POST /basket
- GET /basket/{userName}, DELETE /basket/{userName}, POST /basket/checkout

Using AWS Lambda as the backend integration (basket/index.js). The full stack will be in the next section for better understanding.

```
     const apigw2 = new LambdaRestApi(this, "basketApi", {
          proxy: false,
          restApiName: "Basket Service",
          handler: bFunction,
        });
    
        const basket = apigw.root.addResource("basket");
        basket.addMethod("GET");
        basket.addMethod("POST");
    
        const singlebasket = basket.addResource("{userName}");
        singlebasket.addMethod("GET");
        singlebasket.addMethod("DELETE");
```
