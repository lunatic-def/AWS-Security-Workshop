---
title: "Lambda NodeJS function and SQS queue"
date: "`r Sys.Date()`"
weight: 6
chapter: false
pre: " <b> f. </b> "
---

**API flow for orders microservice api gateway**

```
  GET /order -> GetAllOrder

//Single order with userName parameter - resource  name

  GET /order/{userName} -> GetBasket
  expected request: xxx/order/TestuserName?date=timestamp

```

- [example lambda & apigw proxy event](https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway.html)

**1. Create a another file which contain the necessary packages named "package.json"**
![1](/FCJ2024-Mission2/images/4-order/o1.png)

- Download the packages api:
  ![3.1](/FCJ2024-Mission2/images/4-order/o2.png)
  ![3](/FCJ2024-Mission2/images/4-order/o3.png)

- Develop lambda production functions:

_Declare dynamodb service client object to call for dynamodb table_

```
// Create an Amazon DynamoDB service client object.
const ddbClient = new DynamoDBClient();
```

**3. Switch case event.httpMethod**
**Events switch cases** 
```
 if (event.Records != null) {
        await Invoke_SQS(event);
    } else if (event["detail-type"] !== undefined) {
        await Invoke_EventBridge(event);
    } else {
        return await Invoke_ApiGateway(event);
    }
```

- Case 1: If not case 2& 3 -> event come from apigw synchronously -> return a synchronous response -> code and body responce

- Case 2: event.Records exits -> event come from sqs polling -> create a new order -> create and store to table

- Case 3: event.detail-type exits -> the event come from eventbridge's triggered payload (asynchronously)

**case 1**

*- Sample EventBridge event .json*

```
[
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
]
```
*Request sample*
```
{
    "resource": "/order/{userName}",
    "path": "/order/Gidle",
    "httpMethod": "GET",
    "queryStringParameters": {
        "date": "2024-05-20T15:34:28.819Z"
    },
    "multiValueQueryStringParameters": {
        "date": [
            "2024-05-20T15:34:28.819Z"
        ]
    },
    "pathParameters": {
        "userName": "Gidle"
    },
    "body": null,
    "isBase64Encoded": false
}
```
- Get all order "/order"
- Get order by userName "/order/{userName}

```
const Invoke_ApiGateway = async (event) => {
    let body;

    try {
      switch (event.httpMethod) {
        case "GET":
          if (event.pathParameters != null) {
            body = await GetOrder(event);
          } else {
            body = await GetAllOrder(event);
          }
          break;
        default:
          throw new Error(`Unsupported route: "${event.httpMethod}"`);
      }

      console.log(body);
      return {
        statusCode: 200,
        body: JSON.stringify({
          message: `Successfully finished operation: "${event.httpMethod}"`,
          body: body,
        }),
      };
    } catch (e) {
      console.error(e);
      return {
        statusCode: 500,
        body: JSON.stringify({
          message: "Failed to perform operation.",
          errorMsg: e.message,
          errorStack: e.stack,
        }),
      };
    }
}
```

**If exit event.pathParameters -> userName**

```
const GetOrder = async (event) => {
    
    console.log("Get Order");

    try {
        const userName = event.pathParameters.userName;
        const dateex = event.queryStringParameters.date;

        const params = {
          //conditions expression
          KeyConditionExpression: "userName = :userName and #dateAttr = :dateValue",
          ExpressionAttributeNames: {
            "#dateAttr": "date"  // Replace "date" with the actual attribute name
          },
          ExpressionAttributeValues: {
            ":userName": { S: userName },
            ":dateValue": { S: dateex}
          },
            TableName: process.env.DYNAMODB_TABLE_NAME
        };

        const { Items } = await ddbClient.send(new QueryCommand(params));

        console.log(Items);
        return Items.map((item) => unmarshall(item));
    } catch (e) {
      console.log("eat ass");
      console.error(e);
      throw e;
    }
}

const GetAllOrder = async () => {
    console.log(" Get_all_order");

    try {
      const params = {
        TableName: process.env.DYNAMODB_TABLE_NAME,
      };

      const { Items } = ddbClient.send(new ScanCommand(params));

      console.log(Items);
      return Items ? Items.map((item) => unmarshall(item)) : {};
    } catch (e) {
      console.error(e);
      throw e;
    }
}
```

**Case 2 && 3**

[lambda with sqs ](https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html)
![pic](/FCJ2024-Mission2/images/4-order/sqs1.png)

- EventSource mapping:
- Polling event: Consumer poll product for message in batch and then process the batch before returning event batch records. Queue is a type event polling event source can be use for buffering incoming lambda request and support asynchronous request\
- AWS SQS for decouple microservice and processing event asynchronously using queues in durable and resilience way.



**a. Case 2**

![sqs](/FCJ2024-Mission2/images/4-order/topo3.png)
[sqs](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_sqs.Queue.html)

[lamdba sqs event-source](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_lambda_event_sources.SqsEventSource.html)

[evenbridge sqs event-target](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_events_targets.SqsQueue.html)
- SQS queue: 
  - visibilityTimeout: Timeout of processing a single message.
- Lambda event source: An event source mapping is an AWS Lambda resource that reads from an event source and invokes a Lambda function. You can use event source mappings to process items from a stream or queue in services that don't invoke Lambda functions directly.Available for SQS,S3,SNS,DynamoDB,Kinesis,Kafka,StreamEventSource
- Evenbridge sqs event-target: Use an SQS Queue as a target for Amazon EventBridge rules.

```
import { SqsEventSource } from "aws-cdk-lib/aws-lambda-event-sources";
import { Queue } from "aws-cdk-lib/aws-sqs";
import { Duration } from "aws-cdk-lib";

//create queue
const order_queue = new Queue(this, 'order_queue', {
    queueName: 'OrderQueue',
    visibilityTimeout: Duration.seconds(30)
});
//add event to function
oFunction.addEventSource(new SqsEventSource(order_queue, {
  // number of records lambda receive from sqs service from event source mapping
  batchSize: 1 //read message from sqs 1 by 1, Default 10
}));

```

**Lambda function for SQS event source mapping polling invocation**
*- Sample SQS message event:*
```
{
    "Records": [
        {
            "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
            "receiptHandle": "AQEBwJnKyrHigUMZj6rYigCgxlaS3SLy0a...",
            "body": "Test message.",
            "attributes": {
                "ApproximateReceiveCount": "1",
                "SentTimestamp": "1545082649183",
                "SenderId": "AIDAIENQZJOLO23YVJ4VO",
                "ApproximateFirstReceiveTimestamp": "1545082649185"
            },
            "messageAttributes": {},
            "md5OfBody": "e4e68fb7bd0e697a0ae8f1bb342846b3",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:us-east-2:123456789012:my-queue",
            "awsRegion": "us-east-2"
        },
        {
            "messageId": "2e1424d4-f796-459a-8184-9c92662be6da",
            "receiptHandle": "AQEBzWwaftRI0KuVm4tP+/7q1rGgNqicHq...",
            "body": "Test message.",
            "attributes": {
              ...
        }
    ]
}
```
*Sample event.body*
```
 // expected request :
        { 
          "detail-type\":\"CheckoutBasket\",\"source\":\"com.swn.basket.checkoutbasket\",
          "detail\":{\"userName\":\"swn\",\"totalPrice\":1820, .. 
        }
```

```
const Invoke_SQS = async (event) => {
    console.log(`sqsInvocation function. event : "${event}"`);

    event.Records.forEach(async (record) => {
        console.log('Record: %j', record);

        const checkoutEventRequest = JSON.parse(record.body);

        // create order item into db
        await CreateOrder(checkoutEventRequest.detail);
        // detail object should be checkoutbasket json object
    });
}

const CreateOrder = async (orderrequest) => {

    try {
        console.log(`createOrder function. event : "${orderrequest}"`);

        //get latest date
        orderrequest.date = new Date().toISOString();
        console.log(orderrequest);

        const params = {
            TableName: process.env.DYNAMODB_TABLE_NAME,
            Item: marshall(orderrequest || {})
        };

        const result = await ddbClient.send(new PutItemCommand(params));

        console(result);
        return result;
    }catch (e) {
    console.error(e);
    throw e;
  }
}
```

**b. case 3**

```

const Invoke_EventBridge = async (event) => {
    console.log(`eventBridgeInvocation function. event : "${event}"`);
    await CreateOrder(event.detail);
}
```
