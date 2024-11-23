---
title : "Autonomous Monitoring of Cryptography Activity with KMS"
date : "`r Sys.Date()`"
weight : 1
chapter : false
---
## Overview
Provide the ability to provide tracebility and automatically react to security events occuring in your workload.
- Monitoring key activity metrics, architects 
- Create an autonomous feedback loop which ensures that cloud administrators are adequately informed before a serious event takes place

**Scenerio**

In this labs provide an example scenario of monitoring KMS servie for encryption and decryption activity -> autonomously detect abnormal activity beyond a predefined threhold and respond accordingly:
- CloudTrail: Use for capturing API events within the env
- Cloudwatch Log Groups: save CloudTrails logs 
- Cloudwatch Metric filter: apply filter so we can measure the only the events that matters 
- SNS: send email notification when an event occurs

**Topology**
![1](/AWS-Security-Workshop/images/well_1/topo.png)

## Steps:
- **[Step 1: Deploy web application for encrypt/decrypt testing with ECR](#deploy-application-and-ecr)**
- **[Step 2: Configure CloudTrail for event monitoring](#configure-cloudtrail)**
- **[Step 3: Configure CloudWatch log groups and metric filter ](#configure-cloudwatch-logging-and-alarm)**
- **[Step 4: Testing the workload](#testing-the-workload)**
### Deploy Application and ECR
**1) Create SDK application && ECR:**
**Application**
Application nodejs express:
- Expose a REST API route "/encrypt" and "/decrypt"
- Input: json data
```json
{
    "Name":"Anh La",
    "Text":"Test text for encrypt and decrypt with KMS key"
}
```
- Route "/encrypt" -> app will store the data in RDS and return an Encryption key value for that needed for decrypting 
- Route "/decrypt" -> app ill do the reverse, taking the Encryption key to decrypt the text

```js
function encryptData( KeyId, Plaintext ){
  var promise = new Promise(function(resolve,reject){
    kmsClient.encrypt({ KeyId, Plaintext }, (err, data) => {
      if (err) {
        console.log(err)
        reject(err); // an error occurred
      }
      else {
        const { CiphertextBlob } = data;
        resolve ( CiphertextBlob );
      };
    });
  
  });
  return promise;
};



function decryptData( KeyId, CiphertextBlob ){
  var promise = new Promise(function(resolve,reject){
    kmsClient.decrypt({ CiphertextBlob, KeyId }, (err, data) => {
      if (err) {
        console.log(err)
        reject(err); // an error occurred
      }
      else {
        const { Plaintext } = data;
        resolve ( Plaintext.toString() );
      };
    });
  
  });
  return promise;
};
```

{{% notice note %}}
When a **invalid key** used for decryption purpose, an event on cloudtrail will be created using the ssm:assumed role of the application service role, this will trigger the cloudwatch alert metric -> will go deeper later on
{{% /notice %}}
**2) Create ECR and push application**
![1](/AWS-Security-Workshop/images/well_1/1.1.PNG)
![1](/AWS-Security-Workshop/images/well_1/2-ecr-app.PNG)
![1](/AWS-Security-Workshop/images/well_1/2.1.PNG)
**3) Create RDS, ECS role policy and ECS task,service**
RDS database:
![2](/AWS-Security-Workshop/images/well_1/2.4-rds.PNG)
ECS service application information:
![2](/AWS-Security-Workshop/images/well_1/2.5-ecs.PNG)
![2](/AWS-Security-Workshop/images/well_1/2.5-ecstask-info.PNG)
ECS service roles: allow putting loggroups, create/get KMS key, RDS Secret manger
```js
AssumeRolePolicyDocument:
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: 'sts:AssumeRole'
      Path: /
      Policies:            
        - PolicyName: KMSAccess
          PolicyDocument:
            Version: 2012-10-17
            Statement:
              - Effect: Allow
                Action: '*'
                Resource: !GetAtt KMSKey.Arn
        - PolicyName: SMAccess
          PolicyDocument:
            Version: 2012-10-17
            Statement:
              - Effect: Allow
                Action: 'secretsmanager:GetSecretValue'
                Resource: !Ref RDSSecret    
        - PolicyName: CloudWatchLogs
          PolicyDocument:
            Version: 2012-10-17
            Statement:
              - Effect: Allow
                Action: 'logs:*'
                Resource: !GetAtt ECSCloudWatchLogsGroup.Arn 
```
![2](/AWS-Security-Workshop/images/well_1/2.5-ecs-taskrole.png)

**4) Test simple connection:**

Base ALB DNS get access to application: 
![2](/AWS-Security-Workshop/images/well_1/2.6-alb.PNG)
**Test Encryption**
```shell
curl --header "Content-Type: application/json" --request POST --data '{"Name":"Anh La","Text":"Test clean text for encryption purpose!"}' App-Pattern1-lTZxP9T4MFn7-ACCOUNT-ID.ap-southeast-2.elb.amazonaws.com/encrypt
```
![2](/AWS-Security-Workshop/images/well_1/3-curltext.PNG)
A KMS key is created using the service assumed role account:
![2](/AWS-Security-Workshop/images/well_1/2.6-key.PNG)
![2](/AWS-Security-Workshop/images/well_1/3.1-record.PNG)
### Configure CloudTrail 
**1) Create Cloudtrail 's trail name "Logging-trail" with management events API activity - "Read,Write" and cloudwatch logging enable**

**CloudTrail role**
```js
AssumeRolePolicyDocument:
        Statement:
          - Effect: Allow
            Principal:
              Service: cloudtrail.amazonaws.com
            Action: 'sts:AssumeRole'
      Path: /
      Policies:
        - PolicyName: AWSCloudTrailCreateLogStream
          PolicyDocument:
            Version: 2012-10-17
            Statement:
              - Effect: Allow
                Action: 'logs:CreateLogStream'
                Resource: !GetAtt Pattern1CloudWatchLogGroup.Arn
        - PolicyName: AWSCloudTrailPutLogEvents
          PolicyDocument:
            Version: 2012-10-17
            Statement:
              - Effect: Allow
                Action: 'logs:PutLogEvents'
                Resource: !GetAtt Pattern1CloudWatchLogGroup.Arn

```
![4](/AWS-Security-Workshop/images/well_1/4.1-cloudtrail-mevent.PNG)
![4](/AWS-Security-Workshop/images/well_1/4-cwcloudtrail.PNG)

**CloudWatch logs created by cloudtrail**
![4](/AWS-Security-Workshop/images/well_1/4.2-cwlogs.PNG)
### Configure CloudWatch Logging and Alarm 
1) Create CloudWatch metric filter
![5](/AWS-Security-Workshop/images/well_1/5.PNG)
Filter pattern base on **'eventSource="kms.amazonaws.com'** -> The filter which we created in the previous step will look for all error codes which come from an eventSource of kms.amazonaws.com where the identity of the request matches the ECS Task role ARN.(Which belongs to the application KMS API calling event within cloudtrail)

```shell
{ $.errorCode = "*" && $.eventSource= "kms.amazonaws.com" && $.userIdentity.sessionContext.sessionIssuer.arn= "arn:aws:iam::ACCOUNT-ID:role/App-ECSTaskRole" }
```
![5](/AWS-Security-Workshop/images/well_1/5.1-filterpattern.PNG)
![5](/AWS-Security-Workshop/images/well_1/5.2-assignmetric.PNG)

2) Create metric CloudWatch alarm: assigned threshold > 1

=> Alarm subscribe to SNS email notification alert:
![5](/AWS-Security-Workshop/images/well_1/5.3-metricalarm.PNG)
![5](/AWS-Security-Workshop/images/well_1/5.4-period.PNG)
![5](/AWS-Security-Workshop/images/well_1/5.4-period2.PNG)
![5](/AWS-Security-Workshop/images/well_1/5.5-snstopic.PNG)
![5](/AWS-Security-Workshop/images/well_1/5.5-snstopic2.PNG)
![5](/AWS-Security-Workshop/images/well_1/5.6-snsemail.PNG)
### Testing the workload
Decrypt with the wrong key example:
![6](/AWS-Security-Workshop/images/well_1/6.1-wrongkey.PNG)
CloudWatch API event: **'errorCode="IncorrectKeyException"'**
![7](/AWS-Security-Workshop/images/well_1/7-API_falsedecrypt.PNG)
SNS email notification:
![7](/AWS-Security-Workshop/images/well_1/7.1-emailresult.PNG)
CloudWatch alarm:
![7](/AWS-Security-Workshop/images/well_1/7.2-cwlogs.PNG)
