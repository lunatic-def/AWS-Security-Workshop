---
title: "Basket Checkout result + podman"
date: "`r Sys.Date()`"
weight: 5
chapter: false
pre: " <b> e. </b> "
---

In this section we will  continue testing basket functions: 

//Checkout basket flow

  POST /basket/checkout -> CheckOut

- Testing stacks for basket service: 
```
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
      //add target(order service) to rule
      CheckoutRule.addTarget(new LambdaFunction(ofunction));
```

- Order lambda function for testing: 
```
exports.handler = async function (event) {
  console.log("request", JSON.stringtify(event, undefined, 2));
  return {
    statusCode: 200,
    headers: { "Content type": "text/plain" },
    body: `Hello from Order service !You 've hit ${event.path}\n`
  };
}

```
- Dynamodb with "userName" as the primary key:
![pic](/FCJ2024-Mission2/images/4-order/dynamodb.png)
- API Gateway result method:
![pic](/FCJ2024-Mission2/images/4-order/apigw.png)
![pic](/FCJ2024-Mission2/images/4-order/apigwb.png)
- Lambda stack:
![pic](/FCJ2024-Mission2/images/4-order/lambda1.png)
- "CheckoutBasketRole" Event bus:
![pic](/FCJ2024-Mission2/images/4-order/eventbus.png)
![pic](/FCJ2024-Mission2/images/4-order/eventbus2.png)

**Testing CheckoutBasket EventBridge Async Flow**

{{< video src="vid" width="1000px" >}}