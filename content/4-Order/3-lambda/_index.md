---
title: "Lambda"
date: "`r Sys.Date()`"
weight: 3
chapter: false
pre: " <b> c. </b> "
---

- [Api reference](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_lambda_nodejs-readme.html)
- [basic example](https://github.com/aws-samples/aws-cdk-examples/blob/main/typescript/api-cors-lambda-crud-dynamodb/index.ts)


1. Add all the necessary lib for aws lambda using nodejs function and also dynamodb table

```
import {
  NodejsFunction,
  NodejsFunctionProps,
} from "aws-cdk-lib/aws-lambda-nodejs";
import { Runtime } from "aws-cdk-lib/aws-lambda";
import { ITable } from "aws-cdk-lib/aws-dynamodb";
import { Construct } from "constructs";
import { join } from "path";
```

2. Define dynamodb interface

```
interface DynamodbProps {
  otable: ITable;
}
```

3. Define Lambda Nodejs "Product" function

```
private OrderFunction(otable: ITable): NodejsFunction {
    // Define NodeJS function properties
    const props: NodejsFunctionProps = {
      bundling: {
        externalModules: ["aws-sdk"],
      },
      environment: {
        PRIMARY_KEY: "userName",
        SORT_KEY: "date",
        DYNAMODB_TABLE_NAME: otable.tableName,
      },
    };
    const orderfunction = new NodejsFunction(this, "Order-function", {
      entry: join(__dirname, `/../nodejs_src/order/index.js`),
      ...props,
    });
    
    otable.grantReadWriteData(orderfunction);
    return orderfunction;
  }
```

- Define the lambda_nodejs properties:
  - bundling: used to configure the process of packaging the required dependencies and code into a single deployment. In this case specific the external module that need to be included (aws-sdk module) -> indicating that it should be included in the bundled deployment artifact for the Nodejs function
  - environment: define the dynamodb variable use for deployment
  - runtime: Lambda function runtime environment. In this case NodeJS 16
- Define the lambda_nodejs function:
  - entry: path of lambda handler
  - props: lambda previously defined properties
- Grant dynamodb read write permission for lambda function 

4. Final code
```
import {
  NodejsFunction,
  NodejsFunctionProps,
} from "aws-cdk-lib/aws-lambda-nodejs";
import { Runtime } from "aws-cdk-lib/aws-lambda";
import { ITable } from "aws-cdk-lib/aws-dynamodb";
import { Construct } from "constructs";
import { join } from "path";

interface DynamodbProps {
  otable: oTable;
}

export class LambdaFunction extends Construct {
  public readonly oFunction: NodejsFunction;

  constructor(scope: Construct, id: string, dbprops: DynamodbProps) {
    super(scope, id);

    this.oFunction = this.BasketFunction(DynamodbProps.otable);

  }
  private OrderFunction(otable: ITable): NodejsFunction {
    // Define NodeJS function properties
    const props: NodejsFunctionProps = {
      bundling: {
        externalModules: ["aws-sdk"],
      },
      environment: {
        PRIMARY_KEY: "userName",
        SORT_KEY: "date",
        DYNAMODB_TABLE_NAME: otable.tableName,
      },
    };
    const orderfunction = new NodejsFunction(this, "Order-function", {
      entry: join(__dirname, `/../nodejs_src/order/index.js`),
      ...props,
    });
    
    otable.grantReadWriteData(orderfunction);
    return orderfunction;
  }
}

```
=>Finnaly this class return NodejsFunction variable.

