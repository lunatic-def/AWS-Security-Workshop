---
title: "Lambda NodeJS function"
date: "`r Sys.Date()`"
weight: 3
chapter: false
pre: " <b> c. </b> "
---

- [example lambda & apigw proxy event](https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway.html)

**1. Create a another file which contain the necessary packages named "package.json"**
![1](/FCJ2024-Mission2/images/2-product/1.JPG)

- Add content:
![2](/FCJ2024-Mission2/images/2-product/2.JPG)

- Download the packages api:
![3.1](/FCJ2024-Mission2/images/2-product/3.1.JPG)
![3](/FCJ2024-Mission2/images/2-product/3.JPG)

- Develop lambda production functions:

**2. Declare dynamodb service client object to call for dynamodb table**
```
const ddbClient = new DynamoDBClient();
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
- Response example format:
```
var response = {
      "statusCode": 200,
      "headers": {
        "Content-Type": "application/json"
      },
      "isBase64Encoded": false,
      "multiValueHeaders": { 
        "X-Custom-Header": ["My value", "My other value"],
      },
      "body": "{\n  \"TotalCodeSize\": 104330022,\n  \"FunctionCount\": 26\n}"
    }
```
**4. Deploy the switch case event "GET"**
```
 switch (event.httpMethod) {
      case "GET":
        if (event.queryStringParameters != null) {
          // GET product/1234?category=Phone
          body = await GetProductsByCategory(event);
        } else if (event.queryStringParameters != null) {
          // GET product/{id}
          body = await GetProduct(event.pathParameters.id);
        } else {
          body = await GetAllProducts();
        }
        break;
 }
```
***Working with Items and Attributes of dynamodb.***

***[sdk dynamodb example](https://docs.aws.amazon.com/sdk-for-javascript/v3/developer-guide/dynamodb-examples.html)***

[aws-sdk dynamodb api](https://docs.aws.amazon.com/AWSJavaScriptSDK/v3/latest/client/dynamodb/)

[aws-sdk dynamodb-util api](https://docs.aws.amazon.com/AWSJavaScriptSDK/v3/latest/Package/-aws-sdk-util-dynamodb/)


**a. Get product && Get all product**

The function receive the "id" parameter within the event.queryStringParameters.id come form Apigw
- TableName: DNAMODB_TABLE_NAME get from the environment variable of lambda 
- Key:  primary key of the item to retrieve, in this case "id"
=> Dynamodb - GetItemCommand return data match a set of attributes for the item with the given primary key
=> Dynamodb - ScanCommand operation returns one or more items and item attributes by accessing every item in a table or a secondary index

```
// GET product/{id}
const GetProduct = async (productId) => {
  console.log("getProduct");

  try {
    const params = {
      TableName: process.env.DYNAMODB_TABLE_NAME,
      //marshall convert JavaScript object into DynamoDB Record
      Key: marshall({ id: productId }),
    };

    const { Item } = await ddbClient.send(new GetItemCommand(params));

    console.log(Item);
    //unmarshall convert DynamoDB Record into JavaScript object
    // if item is not null unmarshall(Item) else return {}
    return Item ? unmarshall(Item) : {};
  } catch (e) {
    console.error(e);
    throw e;
  }
};
// GET product/
const GetAllProducts = async () => {
  console.log("getAllProducts");
  try {
    const params = {
      TableName: process.env.DYNAMODB_TABLE_NAME,
    };

    const { Items } = await ddbClient.send(new ScanCommand(params));

    console.log(Items);
    return Items ? Items.map((item) => unmarshall(item)) : {};
  } catch (e) {
    console.error(e);
    throw e;
  }
};
```
**b. Get product by category**

=> Dynamodb-QueryCommand: Query returns all items with that partition key value.
```
const GetProductsByCategory = async (event) => {
  console.log("getProductsByCategory");
  try {
    // GET product/1234?category=Phone
    const productId = event.pathParameters.id;
    const category = event.queryStringParameters.category;

    const params = {
      KeyConditionExpression: "id = :productId",
      FilterExpression: "contains (category, :category)",
      ExpressionAttributeValues: {
        ":productId": { S: productId },
        ":category": { S: category },
      },
      TableName: process.env.DYNAMODB_TABLE_NAME,
    };

    const { Items } = await ddbClient.send(new QueryCommand(params));

    console.log(Items);
    return Items.map((item) => unmarshall(item));
  } catch (e) {
    console.error(e);
    throw e;
  }
};

```

**5. Deploy the switch case event "POST"**
```
 case "POST":
        body = await CreateProduct(event);
        break;
```
**Create product**
The function receive the parameter event.body come form Apigw:

*example*
```
{
    "id":0309,
    "name":"NewItem"
}
```
- TableName: DNAMODB_TABLE_NAME get from the environment variable of lambda 
- Item: A map of attribute name/value pairs, one for each attribute. Only the primary key attributes are required; 

=> Dynamodb - PutItemCommand: Creates a new item, or replaces an old item with a new item. If an item that has the same primary key as the new item already exists in the specified table, the new item completely replaces the existing item.
{{% notice info %}}
PutItemCommand will replace the existing items to prevent that we will use  uuidv4() to generate new "id" for product
{{% /notice %}}
```
const CreateProduct = async (event) => {
  console.log(`createProduct function. event : "${event}"`);
  try {
    const productRequest = JSON.parse(event.body);
    // set productid
    const productId = uuidv4();
    productRequest.id = productId;

    const params = {
      TableName: process.env.DYNAMODB_TABLE_NAME,
      Item: marshall(productRequest || {}),
    };

    const createResult = await ddbClient.send(new PutItemCommand(params));

    console.log(createResult);
    return createResult;
  } catch (e) {
    console.error(e);
    throw e;
  }
};
```
**6. Deploy the switch case event "PUT"**
```
case "PUT":
        body = await UpdateProduct(event);
        break;
```
**Update Product**

The function receive the parameter event.body come form Apigw:

*example*
```
{
  //Key
  "id":10,
  //Attribute
  "name":"myproduct",
  "price":123
}
```
=> Dynamodb - UpdateItemCommand: Edits an existing item's attributes, or adds a new item to the table if it does not already exist. You can put, delete, or add attribute values. You can also perform a conditional update on an existing item

```
// PUT /product/{id }
const UpdateProduct = async (event) => {
  console.log(`updateProduct function. event : "${event}"`);
  try {
    const requestBody = JSON.parse(event.body);
    const objKeys = Object.keys(requestBody);
    console.log(
      `updateProduct function. requestBody : "${requestBody}", objKeys: "${objKeys}"`
    );

    const params = {
      TableName: process.env.DYNAMODB_TABLE_NAME,
      Key: marshall({ id: event.pathParameters.id }),
      UpdateExpression: `SET ${objKeys
        .map((_, index) => `#key${index} = :value${index}`)
        .join(", ")}`,
      ExpressionAttributeNames: objKeys.reduce(
        (acc, key, index) => ({
          ...acc,
          [`#key${index}`]: key,
        }),
        {}
      ),
      ExpressionAttributeValues: marshall(
        objKeys.reduce(
          (acc, key, index) => ({
            ...acc,
            [`:value${index}`]: requestBody[key],
          }),
          {}
        )
      ),
    };

    const updateResult = await ddbClient. end(new UpdateItemCommand(params));

    console.log(updateResult);
    return updateResult;
  } catch (e) {
    console.error(e);
    throw e;
  }
};
```
**7. Deploy the switch case event "DELETE"**
```
case "DELETE":
    body = await DeleteProduct(event.pathParameters.id); // DELETE /product/{id}
    break;
```
=> Dynamodb - DeleteItemCommand deletes a single item in a table by primary key

```
const DeleteProduct = async (productId) => {
  console.log(`deleteProduct function. productId : "${productId}"`);

  try {
    const params = {
      TableName: process.env.DYNAMODB_TABLE_NAME,
      Key: marshall({ id: productId }),
    };

    const deleteResult = await ddbClient.send(new DeleteItemCommand(params));

    console.log(deleteResult);
    return deleteResult;
  } catch (e) {
    console.error(e);
    throw e;
  }
};
```

**8. Handler return operation**
- statusCode: 200 - SUCCESS
- statusCode: 500 - ERROR

*example response json*
```
{ "message": "Hello from Lambda!" }
{
  "isBase64Encoded": false,
  "statusCode": 200,
  "body": "{ \"message\": \"Hello from Lambda!\" }",
  "headers": {
    "content-type": "application/json"
  }
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