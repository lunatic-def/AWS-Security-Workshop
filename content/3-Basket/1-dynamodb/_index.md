---
title : "Dynamodb table"
date : "`r Sys.Date()`"
weight : 1
chapter : false
pre : " <b> a. </b> "
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
  public readonly btable: ITable;

  constructor(scope: Construct, id: string) {
    super(scope, id);
    this.btable = this.BasketTable(); //return variable
  }

  private BasketTable(): ITable {
    const table = new Table(this, "basket-table", {
      partitionKey: {
        name: "userName",
        type: AttributeType.STRING,
      },
      tableName: "basket",
      billingMode: BillingMode.PAY_PER_REQUEST,
      removalPolicy: RemovalPolicy.DESTROY,
    });
    return table;
  }
}

```
- In this section we will only create dynamodb table for product function: 
    + Table name: product
    + Partition key: userName

**-> This class will return an ITable type of dynamodb**

One person can have many items in their database

*example*
```
basket: Primary key - userName -- items
  item1 - { quantity - color - price - productId - productName}
  item2 - { quantity - color - price - productId - productName}
```
