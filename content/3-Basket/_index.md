---
title : "Basket service"
date : "`r Sys.Date()`"
weight : 3
chapter : false
pre : " <b> 3. </b> "
---

In this step we will create lambda basket service with simple CRUD REST API function and publish checkout event to EventBridge.
![topology](/FCJ2024-Mission2/images/3-basket/topo.png)

**Steps**
1) Create DynamoDB with AWS CDK
2) Create Basket lambda with AWS CDK
3) Create Lambda Basket function with AWS SDK API
4) Create Api gateway