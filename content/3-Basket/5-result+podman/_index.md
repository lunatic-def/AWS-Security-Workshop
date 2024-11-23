---
title: "Result + Podman"
date: "`r Sys.Date()`"
weight: 5
chapter: false
pre: " <b> e. </b> "
---

In this section we will test these first functions: 
  - GET /basket -> GetAllBasket
  - POST /basket -> CreateBasket

//Single basket with userName parameter - resource  name
  - GET /basket/{userName} -> GetBasket
  - DELETE /basket/{userName} -> DeleteBasket
{{% notice info %}}
The testing does not include POST /basket/checkout event, this will be included in the Order service sections "Basket Checkout result + podman "
{{% /notice %}}
- Testing stacks for basket service: 
```
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

      const prop2s: NodejsFunctionProps = {
        bundling: {
          externalModules: ["aws-sdk"],
        },
        environment: {
          PRIMARY_KEY: "userName",
          DYNAMODB_TABLE_NAME: btable.tableName,
          EVENT_SOURCE: "com.swn.basket.checkoutbasket",
          EVENT_DETAILTYPE: "CheckoutBasket",
          EVENT_BUSNAME: "SwnEventBus",
        },
        runtime: Runtime.NODEJS_16_X,
      };
      const bFunction = new NodejsFunction(this, "Basket-function", {
        entry: join(__dirname, `/../nodejs_src/basket/index.js`),
        ...prop2s,
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

      const basketcheckout = basket.addResource('checkout');
      basketcheckout.addMethod("POST");
```


- Dynamodb with "userName" as the primary key:
  ![pic](/FCJ2024-Mission2/images/3-basket/res1.png)
- API Gateway result method:
  ![pic](/FCJ2024-Mission2/images/3-basket/res2.png)
- Lambda stack:
  ![pic](/FCJ2024-Mission2/images/3-basket/res3.png)
- Lambda triggers:
  ![pic](/FCJ2024-Mission2/images/3-basket/res4.png)
- Test event on lambda function with json:

```
{
    "userName": "testusername"
}
```

![pic](/FCJ2024-Mission2/images/3-basket/res5.png)

=> Result SUCCESS

- Test API gateway path:
  ![pic](/FCJ2024-Mission2/images/3-basket/res6.png)

  **_PODMAN_**

**Demo GetAllBasket, GetBasketbyName and CreateBasket**

{{< video src="b1" width="1000px" >}}

**Demo DeleteBasket**

{{< video src="b2" width="1000px" >}}

