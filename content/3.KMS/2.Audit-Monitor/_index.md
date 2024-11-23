---
title: "Audit and monitor KMS"
date: "`r Sys.Date()`"
weight: 2
chapter: false
---

**Main tools in this labs contains:**
- [CloudTrail](#cloudtrail)
- [CloudWatch](#cloudwatch)
- [Access analyzer](#aws-access-analyzer)

## CloudTrail
Track KMS API calls made on keys -> Determine which API was called, who called it and when, what IP address of the caller was ?

1) Cloudtrail track API calling event: 
```shell
aws kms generate-data-key --key-id alias/kms-workshop --key-spec AES_256 --encryption-context project=kms-workshop
```
![4](/AWS-Security-Workshop/images/kms_2/4.png)
![4](/AWS-Security-Workshop/images/kms_2/4.1.png)

## CloudWatch
[Static threshold](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/ConsoleAlarms.html)

Metrics for KMS service and keys -> import key material into a KMS key and set it to expire.
If you click through here you will find the metric "SecondsUntilKeyMaterialExpiration" for the KMS key which was built with imported key material. With this metric you can now build an alarm into CloudWatch to warn you about the expiration of the key material for example.
![4](/AWS-Security-Workshop/images/kms_2/5.png)

## AWS Access Analyzer

To keep access to your KMS based on the least privilege and need-to-have principle

- **AWS IAM Access Analyzer** -> identify the resources in your organization and accounts that are shared with an external entity include AWS KMS keys.
  - Autonomously detect public access once it has been enabled on your account in a specific Region
  - Generates a finding for each instance of a resource-based policy that grants access to a resource within your zone of trust to a principal that is outside your zone of trust
  - Publish all findings in the Access Analyzer dashboard in the IAM console and generates CloudWatch Events for each finding

```json
{
  "source": ["aws.access-analyzer"],
  "detail-type": ["Access Analyzer Finding"]
}
```

### Labs

Setup and Eventbridge rule to be notified of any relevant Access Analyser findings, for example, _if Access Analyzer detects access to AWS KMS key for outside of Your zone of trust_.

1. Create sns topic:

```shell
aws sns create-topic --name kms-workshop-notifications

TOPIC_ARN=REPLACE_WITH_YOUR_TOPIC_ARN
EMAIL_ADDRESS=REPLACE_WITH_YOUR_EMAIL

aws sns subscribe \
    --topic-arn ${TOPIC_ARN} \
    --protocol email \
    --notification-endpoint ${EMAIL_ADDRESS}

```

![1](/AWS-Security-Workshop/images/kms_2/1-sns.png)
![1.1](/AWS-Security-Workshop/images/kms_2/1-1sns.png)

2. Create Eventbridge rule

- create rule to send sms notification about external access analyzer findings.
  ![1.1](/AWS-Security-Workshop/images/kms_2/1.2-rule.png)
  ![1.1](/AWS-Security-Workshop/images/kms_2/1.3-eventpattern.png)
  ![1.1](/AWS-Security-Workshop/images/kms_2/1.4-snstarget.png)
  ![1.1](/AWS-Security-Workshop/images/kms_2/1.5.png)

3. Create Access analyzer for External access analysis within current account
   ![2](/AWS-Security-Workshop/images/kms_2/2-accessanalyzer.png)
4. Test if Access Analyzer generates findings -> public access policy for KMS key
   ![2](/AWS-Security-Workshop/images/kms_2/2.1-key.png)
   ![2](/AWS-Security-Workshop/images/kms_2/2.2-key.png)
   => The call above added a "\*" principal to the key policy, making the key accessible for any AWS principal. From now on, Access Analyzer will detect any public access to your AWS KMS key and generate a finding. The CloudWatch events rule will be invoked and will publish a message to the Amazon SNS topic.

OUTPUTS:
![3](/AWS-Security-Workshop/images/kms_2/3-res.png)
![3](/AWS-Security-Workshop/images/kms_2/3.1.png)
![3](/AWS-Security-Workshop/images/kms_2/3.2.png)

```json
{
  "version": "0",
  "id": "b4f76a53-489d-af80-7152-da2744195fd4",
  "detail-type": "Access Analyzer Finding",
  "source": "aws.access-analyzer",
  "account": "..",
  "time": "2024-07-22T10:09:05Z",
  "region": "ap-southeast-2",
  "resources": [
    "arn:aws:access-analyzer:ap-southeast-2::analyzer/ExternalAccess-ConsoleAnalyzer-d00ca272-a5cc-4be8-a406-ff238ce0fda0"
  ],
  "detail": {
    "version": "1.0",
    "id": "0aad2c61-a82c-43da-b3c7-18c3f771a818",
    "status": "ACTIVE",
    "resourceType": "AWS::KMS::Key",
    "resource": "arn:aws:kms:ap-southeast-2:...:key/4ab85425-3ede-4dd1-9f17-914a7e2f33d7",
    "createdAt": "2024-07-22T10:09:03.496Z",
    "analyzedAt": "2024-07-22T10:09:03.496Z",
    "updatedAt": "2024-07-22T10:09:03.496Z",
    "accountId": "....",
    "region": "ap-southeast-2",
    "principal": { "AWS": "*" },
    "action": [
      "kms:CreateGrant",
      "kms:Decrypt",
      "kms:DescribeKey",
      "kms:Encrypt",
      "kms:GenerateDataKey",
      "kms:GenerateDataKeyPair",
      "kms:GenerateDataKeyPairWithoutPlaintext",
      "kms:GenerateDataKeyWithoutPlaintext",
      "kms:GenerateMac",
      "kms:GetKeyRotationStatus",
      "kms:GetPublicKey",
      "kms:ListGrants",
      "kms:ReEncryptFrom",
      "kms:ReEncryptTo",
      "kms:RetireGrant",
      "kms:RevokeGrant",
      "kms:Sign",
      "kms:Verify",
      "kms:VerifyMac"
    ],
    "condition": {},
    "isDeleted": false,
    "isPublic": true
  }
}
```

{{% notice note %}}
"isPublic":true
{{% /notice %}}
