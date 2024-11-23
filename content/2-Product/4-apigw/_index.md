---
title: "Api gateway"
date: "`r Sys.Date()`"
weight: 4
chapter: false
pre: " <b> d. </b> "
---

[api reference](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_apigateway-readme.html)

Defining API that includes the following HTTP endpoints:

- GET /product, POST /product
- GET /product/{id}, DELETE /product/{id}, PUT /product/{id}

Using AWS Lambda as the backend integration (product/index.js). The full stack will be in the next section for better understanding.

```
      const apigw = new LambdaRestApi(this, "productApi", {
        proxy: false,
        restApiName: "Product Service",
        handler: product_func,
      });
      //root path (/product)
      const productapi = apigw.root.addResource("product");
      productapi.addMethod("GET");
      productapi.addMethod("POST");

      // sub-path (/product/{id})
      const singleproduct = productapi.addResource("{id}");
      singleproduct.addMethod("GET");
      singleproduct.addMethod("PUT");
      singleproduct.addMethod("DELETE");
```
