---
title : "Dynamodb table"
date : "`r Sys.Date()`"
weight : 2
chapter : false
pre : " <b> b. </b> "
---

+ [Api reference](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_dynamodb-readme.html)
+ [basic example](https://github.com/bobbyhadz/aws-cdk-dynamodb-table/blob/cdk-v2/lib/cdk-starter-stack.ts)
+ [aws cdk official github repo](https://github.com/aws/aws-cdk/blob/main/packages/aws-cdk-lib/aws-dynamodb/lib/table.ts)

``` 
import {
  Attribute,
  AttributeType,
  BillingMode,
  ITable,
  Table,
  TableV2,
} from "aws-cdk-lib/aws-dynamodb";
import { RemovalPolicy } from "aws-cdk-lib";
import { Construct } from "constructs";

export class Dynamodb extends Construct {
  public readonly otable: ITable;

  constructor(scope: Construct, id: string) {
    super(scope, id);
    this.otable = this.OrderTable(); //return variable
  }

  private OrderTable(): ITable {
    const table = new Table(this, "sort-table", {
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
      removalPolicy: RemovalPolicy.DESTROY,
    });
    return table;
  }
}

```
- In this section we will only create dynamodb table for product function: 
    + Table name: orders
    + Partition key: userName
    + Sort key: date

**-> This class will return an ITable type of dynamodb**

*example*
```
basket: 
  PrimaryKey: userName 
  SortKey: date -- totalPrice - firstName - lastName - email - address - paymentMethod - cardInfo 
```
