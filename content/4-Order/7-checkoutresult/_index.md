---
title: "CheckoutEvent result + podman"
date: "`r Sys.Date()`"
weight: 7
chapter: false
pre: " <b> g. </b> "
---

- Full testing stack for complete microservice with sqs queue: 
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
import { EventBus, Rule } from "aws-cdk-lib/aws-events";
import { LambdaFunction, SqsQueue } from "aws-cdk-lib/aws-events-targets";
import { SqsEventSource } from "aws-cdk-lib/aws-lambda-event-sources";
import { Queue } from "aws-cdk-lib/aws-sqs";
import { Duration } from "aws-cdk-lib";

export class MicroserviceStack extends cdk.Stack 
{
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
      super(scope, id, props);
      /////////////////////////////////////////////////////////
      // PRODUCT SERVICE //
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
      // Production service api gateway
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

      /////////////////////////////////////////////////////////
      // BASKET SERVICE //
      const btable = new Table(this, "basket-table", {
        partitionKey: {
          name: "userName",
          type: AttributeType.STRING,
        },
        tableName: "basket",
        billingMode: BillingMode.PAY_PER_REQUEST,
        removalPolicy: cdk.RemovalPolicy.DESTROY,
      });

      const props2: NodejsFunctionProps = {
        bundling: {
          externalModules: ["aws-sdk"],
        },
        environment: {
          PRIMARY_KEY: "userName",
          DYNAMODB_TABLE_NAME: btable.tableName,
          EVENT_SOURCE: "com.swn.basket.checkoutbasket",
          EVENT_DETAILTYPE: "CheckoutBasket",
          EVENT_BUSNAME: "EventBus",
        },
        runtime: Runtime.NODEJS_16_X,
      };
      const bFunction = new NodejsFunction(this, "Basket-function", {
        entry: join(__dirname, `/../nodejs_src/basket/index.js`),
        ...props2,
      });
      btable.grantReadWriteData(bFunction);
      // Basket service api gateway
      /*
        GET /basket
        POST /basket (checkout usecase)

        GET /basket/{userName}
        DELETE /basket/{userName}
    */
      const apigw2 = new LambdaRestApi(this, "basketApi", {
        proxy: false,
        restApiName: "Basket Service",
        handler: bFunction,
      });

      const basket = apigw2.root.addResource("basket");
      basket.addMethod("GET");
      basket.addMethod("POST");

      const singlebasket = basket.addResource("{userName}");
      singlebasket.addMethod("GET");
      singlebasket.addMethod("DELETE");

      const basketcheckout = basket.addResource("checkout");
      basketcheckout.addMethod("POST");
      /////////////////////////////////////////////////////////
      // ORDER SERVICE //
      // orders table
      const otable = new Table(this, "sort-table", {
        partitionKey: {
          name: "userName",
          type: AttributeType.STRING,
        },
        sortKey: {
          name: "date",
          type: AttributeType.STRING,
        },
        tableName: "orders",
        billingMode: BillingMode.PAY_PER_REQUEST,
        removalPolicy: cdk.RemovalPolicy.DESTROY,
      });
      //lambda
      const props3: NodejsFunctionProps = {
        bundling: {
          externalModules: ["aws-sdk"],
        },
        environment: {
          PRIMARY_KEY: "userName",
          SORT_KEY: "date",
          DYNAMODB_TABLE_NAME: otable.tableName,
        },
      };
      const ofunction = new NodejsFunction(this, "Order-function", {
        entry: join(__dirname, `/../nodejs_src/order/index.js`),
        ...props3,
      });
      otable.grantReadWriteData(ofunction);

      //api gateway
      const apigw3 = new LambdaRestApi(this, "orderApi", {
        proxy: false,
        restApiName: "Order Service",
        handler: ofunction,
      });
      const order = apigw3.root.addResource("order");
      order.addMethod("GET");
      const singleorder = order.addResource("{userName}");
      singleorder.addMethod("GET");

      // Eventbus
      //create eventbus
      const bus = new EventBus(this, "EventBus", {
        eventBusName: "EventBus",
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
        },
      });
      
      // grant permission to basket function to create event to bus
      bus.grantPutEventsTo(bFunction);

      //sqs queue
      const order_queue = new Queue(this, 'order_queue', {
        queueName: 'OrderQueue',
        visibilityTimeout: Duration.seconds(30)
      });
      //add event to function
      ofunction.addEventSource(new SqsEventSource(order_queue,{batchSize: 1}));

      //add target(order service) to rule
      CheckoutRule.addTarget(new SqsQueue(order_queue));
    }// end of contruct
}//end of class
```

**Testing EventSource Mapping and Polling Invocation**
{{< video src="test1" width="1000px" >}}

**Testing CheckoutBasket EventBridge Async Flow**
{{< video src="test2" width="1000px" >}}

**Testing Order service Api Gateway Sync Flow**
{{< video src="test3" width="1000px" >}}