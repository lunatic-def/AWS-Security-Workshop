---
title: "Result + Podman"
date: "`r Sys.Date()`"
weight: 5
chapter: false
pre: " <b> e. </b> "
---
- Testing stacks for product service: 
```
import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import { AttributeType, BillingMode, Table } from 'aws-cdk-lib/aws-dynamodb';
import { Runtime } from "aws-cdk-lib/aws-lambda";
import {
    NodejsFunction,
    NodejsFunctionProps
} from "aws-cdk-lib/aws-lambda-nodejs";
import { join } from "path";
import { LambdaRestApi } from "aws-cdk-lib/aws-apigateway";

export class MicroserviceStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
      super(scope, id, props);

      const ptable = new Table(this, "product-table", {
        partitionKey: {
          name: "id",
          type: AttributeType.STRING,
        },
        tableName: "product",
        removalPolicy: cdk.RemovalPolicy.DESTROY,
        billingMode: BillingMode.PAY_PER_REQUEST,
      });

      const product_prop: NodejsFunctionProps = {
        bundling: {
          externalModules: ["aws-sdk"],
        },
        environment: {
          PRIMARY_KEY: "id",
          DYNAMODB_TABLE_NAME: ptable.tableName,
        },
        runtime: Runtime.NODEJS_16_X,
      };

      const product_func = new NodejsFunction(this, "product_function", {
        entry: join(__dirname, "/../nodejs_src/product/index.js"),
        ...product_prop,
      });

      ptable.grantReadWriteData(product_func);
    // Single product with id parameter
    /*
        GET /product
        POST /product

        GET /product/{id}
        PUT /product/{id}
        DELETE /product/{id}
    */

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
    }
}
```


- Dynamodb with "id" as the primary key:
  ![pic](/FCJ2024-Mission2/images/2-product/res1.jpg)
- API Gateway result method:
  ![pic](/FCJ2024-Mission2/images/2-product/res2.jpg)
- Lambda stack:
  ![pic](/FCJ2024-Mission2/images/2-product/res3.jpg)
- Lambda function:
  ![pic](/FCJ2024-Mission2/images/2-product/res4.jpg)
- Lambda triggers:
  ![pic](/FCJ2024-Mission2/images/2-product/res5.jpg)
- Test event on lambda function with json:

```
{
    "id": "test"
    "name":"testname"
}
```

![pic](/FCJ2024-Mission2/images/2-product/res6.jpg)
![pic](/FCJ2024-Mission2/images/2-product/res7.jpg)

=> Result SUCCESS

- Test API gateway path:
  ![pic](/FCJ2024-Mission2/images/2-product/res8.jpg)
- Test with GET method in browser -> result with empty body reason for not having items on dynamodb table
  ![pic](/FCJ2024-Mission2/images/2-product/res9.jpg)
  **_PODMAN_**

**Demo GetAllProduct and CreateProduct**

{{< video src="1" width="1000px" >}}

**Demo GetProductbyID and UpdateProduct**

{{< video src="2" width="1000px" >}}

**Demo DeleteProduct**

{{< video src="3" width="1000px" >}}
