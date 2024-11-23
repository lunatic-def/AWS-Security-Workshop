---
title: "Lambda NodeJS function"
date: "`r Sys.Date()`"
weight: 3
chapter: false
pre: " <b> c. </b> "
---
**API flow for basket microservice api gateway**
```
  GET /basket -> GetAllBasket
  POST /basket -> CreateBasket

//Single basket with userName parameter - resource  name
  GET /basket/{userName} -> GetBasket
  DELETE /basket/{userName} -> DeleteBasket

//Checkout basket flow
  POST /basket/checkout -> CheckOut

```

- [example lambda & apigw proxy event](https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway.html)

**1. Create a another file which contain the necessary packages named "package.json"**
![1](/FCJ2024-Mission2/images/3-basket/in3.png)

- Add content:
![2](/FCJ2024-Mission2/images/2-product/2.JPG)

- Download the packages api:
![3.1](/FCJ2024-Mission2/images/3-basket/in1.png)
![3](/FCJ2024-Mission2/images/3-basket/in2.png)

- Develop lambda production functions:

**2. Declare dynamodb service client object to call for dynamodb table and eventbridge client object to create an event**
```
// Create an Amazon DynamoDB service client object.
const ddbClient = new DynamoDBClient();
// Create an Amazon EventBridge service client object.
const ebClient = new EventBridgeClient();
```
**3. Switch case event.httpMethod to perform web CRUD operations** 
- Event httpd example .json
[link](https://github.com/awsdocs/aws-lambda-developer-guide/blob/main/sample-apps/nodejs-apig/event.json)

```
{
    "resource": "/",
    "path": "/",
    "httpMethod": "GET",
    "headers": {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        ...
    }
    "queryStringParameters": null,
    "multiValueQueryStringParameters": null,
    "pathParameters": null,
    "stageVariables": null,
    "requestContext": {
        "resourceId": "2gxmpl",
        "resourcePath": "/",
        "httpMethod": "GET",
        "extendedRequestId": "JJbxmplHYosFVYQ=",
        "requestTime": "10/Mar/2020:00:03:59 +0000",
        "path": "/Prod/",
    }
}
```

**4. Deploy the switch case event "GET"**
```
 switch (event.httpMethod) {
        case "GET":
            if (event.pathParameters != null) {
                body = await GetBasket(event.pathParameters.userName);
            } else {
                body = await GetAllBasket();
            }
        break;
 }
```
***Working with Items and Attributes of dynamodb.***

***[sdk dynamodb example](https://docs.aws.amazon.com/sdk-for-javascript/v3/developer-guide/dynamodb-examples.html)***

[aws-sdk dynamodb api](https://docs.aws.amazon.com/AWSJavaScriptSDK/v3/latest/client/dynamodb/)

[aws-sdk dynamodb-util api](https://docs.aws.amazon.com/AWSJavaScriptSDK/v3/latest/Package/-aws-sdk-util-dynamodb/)


**Get basket && Get all basket**

The function receive the "userName" parameter within the event.queryStringParameters.userName come from Apigw
- TableName: DNAMODB_TABLE_NAME get from the environment variable of lambda 
- Key:  primary key of the item to retrieve, in this case "userName"

=> Dynamodb - GetItemCommand return data match a set of attributes for the item with the given primary key

=> Dynamodb - ScanCommand operation returns one or more items and item attributes by accessing every item in a table or a secondary index

```
// GET basket/{userName}
const GetBasket = async (userName) => {
        console.log("getBasket");

        try {
            const params = {
                TableName: process.env.DYNAMODB_TABLE_NAME,
                Key: marshall({ userName: userName })
            };

            const { result } = await ddbClient.send(new GetItemCommand(params))
            console.log(result);
            return result ? unmarshall(result) : {};
        } catch (err) {
            console.error(err);
            throw err;
        }
    }
    
    const GetAllBasket = async () => {
        console.log("GetAll-Basket");

        try {
            const params = {
                TableName: process.env.DYNAMODB_TABLE_NAME,
            }

            const { result } = await ddbClient.send(new ScanCommand(params));

            console.log(result);
            return result ? unmarshall(result) : {};
        } catch (err) {
            console.error(err);
            throw err;
        }
    }
```

**5. Deploy the switch case event "POST"**
```
case "POST":
            if (event.path == "/basket/checkout") {
                body = await CheckOut(event);
            } else {
                body = await CreateBasket(event);
            }
        break;
```


=> Dynamodb - PutItemCommand: Creates a new item, or replaces an old item with a new item. If an item that has the same primary key as the new item already exists in the specified table, the new item completely replaces the existing item.
{{% notice info %}}
PutItemCommand will replace the existing items to prevent that we will use  uuidv4() to generate new "id" for product
{{% /notice %}}



```
 const CreateBasket = async (event) => {
        console.log(`createBasket function. event : "${event}"`);

        try {
            const tableRequest = JSON.parse(event.body);

            const params = {
                TableName: process.env.DYNAMODB_TABLE_NAME,
                Item: marshall(tableRequest || {})
            };

            const result = await ddbClient.send(new PutItemCommand(params));
            console.log(result);
        } catch (e) {
            console.error(e);
            throw e;
        }
    }
```
[EventBridge api reference](https://docs.aws.amazon.com/AWSJavaScriptSDK/v3/latest/client/eventbridge/)

[Sample PutEvents request && responce](https://docs.aws.amazon.com/eventbridge/latest/APIReference/API_PutEvents.html)

[Examples](https://docs.aws.amazon.com/sdk-for-javascript/v3/developer-guide/javascript_eventbridge_code_examples.html)

=> EventBridge - PutEventsCommand: Sends custom events to Amazon EventBridge so that they can be matched to rules.

- Checkout event with the following steps:
  1) Get request basket with items
  2) Create a an event json object with basket items -> calculate the price and prepare the order (json) to send to order service
  3) Publish event to EventBridge -> Subscribe to order service
      - EVENT_SOURCE: "com.swn.basket.checkoutbasket"
      - EVENT_DETAILTYPE: "CheckoutBasket"
      - EVENT_BUSNAME: "EventBus"
  4) Remove the basket

- Expected request payload: 
```
{
  userName: testusername,
  attributes: [
    firstName,
    lastName,
    email,
    ...
  ]
}
```
**- Request format**
```
{
      "Source": "com.swn.basket.checkoutbasket",
      "Detail": "{ \"username\": \"swn\", \"basket\": \"phone1\" }",
      "Resources": [
        "resource1",
        "resource2"
      ],
      "DetailType": "CheckoutBasket",
      "EventBusName": "SwnEventBus"
    },
    {
      "Source": "com.swn.basket.checkoutbasket",
      "Detail": "{ \"username\": \"swn\", \"basket\": \"phone2\" }",
      "Resources": [
        "resource1",
        "resource2"
      ],
      "DetailType": "CheckoutBasket",
      "EventBusName": "SwnEventBus"
}
```

```
const CheckOut = async (event) => {
        console.log("CheckOutBasket");
        const request = JSON.parse(event.body);

        if (request == null || request.userName == null) {
            throw new Error(`userName should exist in checkout Request: "${request}"`);
        }

        //1. Get request basket
        const basket = await GetBasket(request.userName);

        //2. Calculate the price within the basket, prepare json order to send 
        var payload = PrepareOrderPayload(request, basket);

        //3. Public event to eventbridge
        const publishedevent = await PublicCheckOutEvent(payload);

        //4. remove the checkout basket
        await DeleteBasket(request.userName);
    }

const PrepareOrderPayload = (request, basket) => {
        console.log("prepareOrderPayload");
        try {
          if (basket == null || basket.items == null) {
            throw new Error(`basket should exist in items: "${basket}"`);
          }

          let total = 0;
          basket.items.forEach(
            (item) => (totalPrice = totalPrice + item.price)
          );
          request.totalPrice = totalPrice;
          console.log(request);

          // copies all properties from basket into checkoutRequest
          Object.assign(request, basket);
          console.log(
            "Success prepareOrderPayload, orderPayload:",
            request
          );
          return request;
        } catch (e) {
          console.error(e);
          throw e;
        }
    }

    //public event to eventbrigde
    const PublicCheckOutEvent = async (payload) => {
        console.log(
            "publishCheckoutBasketEvent with payload :",
            payload
        );

        try {
          // eventbridge parameters for setting event to target system
          const params = {
            Entries: [
              {
                Source: process.env.EVENT_SOURCE,
                Detail: JSON.stringify(payload),
                DetailType: process.env.EVENT_DETAILTYPE,
                Resources: [],
                EventBusName: process.env.EVENT_BUSNAME
              }
            ]
          };

          const data = await ebClient.send(new PutEventsCommand(params));

          console.log("Success, event sent; requestID:", data);
          return data;
        } catch (e) {
          console.error(e);
          throw e;
        }
        
    }
```

**6. Deploy the switch case event "DELETE"**

```
case "DELETE":
    body = await DeleteBasket(event.pathParameters.userName);
    break;
```
=> Dynamodb - DeleteItemCommand deletes a single item in a table by primary key

```
const DeleteBasket = async (userName) => {
        console.log(`deleteBasket function. userName : "${userName}"`);
        try {
            const params = {
                TableName: process.env.DYNAMODB_TABLE_NAME,
                Key: marshall({userName: userName})
            }

            const result = await ddbClient.send(new DeleteItemCommand(params));
            console.log(result);

            return result;

        } catch (e) {
            console.error(e);
            throw e;
        }
    }
```

**8. Handler return operation**
- statusCode: 200 - SUCCESS
- statusCode: 500 - ERROR

*example response json*
```
HTTP/1.1 200 OK
x-amzn-RequestId: <RequestId>
Content-Type: application/x-amz-json-1.1
Content-Length: <PayloadSizeBytes>
Date: <Date>

{
    "FailedEntryCount": 0, 
    "Entries": [
        {
            "EventId": "11710aed-b79e-4468-a20b-bb3c0c3b4860"
        }, 
        {
            "EventId": "d804d26a-88db-4b66-9eaf-9a11c708ae82"
        }
    ]
}
```

```
    return {
        statusCode: 200,
        body: JSON.stringify({
          message: `Successfully finished operation: "${event.httpMethod}"`,
          body: body
        })
      };

    } catch (e) {
    console.error(e);
    return {
      statusCode: 500,
      body: JSON.stringify
      ({
        message: "Failed to perform operation.",
        errorMsg: e.message,
        errorStack: e.stack,
      })
    };
```