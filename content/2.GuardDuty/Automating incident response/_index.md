---
title: "Automating incident response"
date: "`r Sys.Date()`"
weight: 1
chapter: false
---

**Scenario:**
An automated incident response playbook and execute it when a compromised instance is detected via GuardDuty including:

- Isolated the compromised instance from accessing the internet and only opened the neccessary connection used for investigating.
- Create a snapshot of the instance.
- Prevent the instance from being deleted.

The adversary was able to execute arbitrary code on the compromised instance by exploiting another vulnerability that existed within the instance

The adversary continue to perform:

- Install a third-party vpn to connect to Command&Control center
- Manipulate target for illegal actions (bit-coin mining)
- UnauthoriedAccess, Backdoor, Trojan

## Lambda response

**[Step 1: setups infastructure](#setups)**

**[Step 2: create restricted policy and group](#create-restricted-policy-and-groups)**

**[Step 3: create lambda function](#create-lambda-function)**

**[Step 4: test lambda function](#test-lambda-function)**

**[Step 5: create eventbridge rule to trigger lambda function](#eventbridge-rule)**

**[Step 6: stimulate the attack](#stimulate-attack)**

![1](/AWS-Security-Workshop/images/gd_1/Architecture.png)

### Setups

**1) Create VPC and EC2 instances**
![1](/AWS-Security-Workshop/images/gd_1/1-VPC.PNG)
![1](/AWS-Security-Workshop/images/gd_1/2-ec2.PNG)
**Basic-linux Target - Security groups**
![1](/AWS-Security-Workshop/images/gd_1/3-linux-sg.PNG)
![1](/AWS-Security-Workshop/images/gd_1/3.1-linux-sg.PNG)

### Create restricted policy and groups

- When a compromised instance is identified:
  - The user using the instance will be add to restricted group to quarantize actions, prevent from deleting the instance and creating any other actions.
  - The compromised instance will be isolated

1. Create sg only allow the connection of Forensics groups (SSH & RDB)
   ![1](/AWS-Security-Workshop/images/gd_1/5-forensic-sg.PNG)
2. Create user group with restricted policy "Deny-termination-of-isolated-instances"
   Policy:
   ![1](/AWS-Security-Workshop/images/gd_1/5-deny-termination.PNG)
   Group:
   ![1](/AWS-Security-Workshop/images/gd_1/6.PNG)
   ![1](/AWS-Security-Workshop/images/gd_1/6-1.PNG)

### Create lambda function

1. Create role to assign to lambda function: allow ec2 and cloudwatch logs
   ![1](/AWS-Security-Workshop/images/gd_1/7.PNG)
2. Create lambda func using python with "ec2instance-containment-with-forensics-role"
   ![1](/AWS-Security-Workshop/images/gd_1/8.PNG)

Python code function:

```python
import boto3, json
import time
from datetime import date
from botocore.exceptions import ClientError
import os

def lambda_handler(event, context):
    response = 'Error remediating the security finding.'
    try:
        # Gather Instance ID from CloudWatch event
        instanceID = event['detail']['resource']['instanceDetails']['instanceId']
        print('## INSTANCE ID: %s' % (instanceID))

        # Get instance details
        client = boto3.client('ec2')
        ec2 = boto3.resource('ec2')
        instance = ec2.Instance(instanceID)
        instance_description = client.describe_instances(InstanceIds=[instanceID])
        print('## INSTANCE DESCRIPTION: %s' % (instance_description))

        #-------------------------------------------------------------------
        # Protect instance from termination
        #-------------------------------------------------------------------
        ec2.Instance(instanceID).modify_attribute(
        DisableApiTermination={
            'Value': True
        })
        ec2.Instance(instanceID).modify_attribute(
        InstanceInitiatedShutdownBehavior={
            'Value': 'stop'
        })

        #-------------------------------------------------------------------
        # Create tags to avoid accidental deletion of forensics evidence
        #-------------------------------------------------------------------
        ec2.create_tags(Resources=[instanceID], Tags=[{'Key':'status', 'Value':'isolated'}])
        print('## INSTANCE TAGS: %s' % (instance.tags))

        #------------------------------------
        ## Isolate Instance
        #------------------------------------
        print('quarantining instance -- %s, %s' % (instance.id, instance.instance_type))

        # Change instance Security Group attribute to terminate connections and allow Forensics Team's access
        instance.modify_attribute(Groups=[os.environ['ForensicsSG']])
        print('Instance ready for root cause analysis -- %s, %s' % (instance.id,  instance.security_groups))

        #------------------------------------
        ## Create snapshots of EBS volumes
        #------------------------------------
        description= 'Isolated Instance:' + instance.id + ' on account: ' + event['detail']['accountId'] + ' on ' + date.today().strftime("%Y-%m-%d  %H:%M:%S")
        SnapShotDetails = client.create_snapshots(
            Description=description,
            InstanceSpecification = {
                'InstanceId': instanceID,
                'ExcludeBootVolume': False
            }
        )
        print('Snapshot Created -- %s' % (SnapShotDetails))

        response = 'Instance ' + instance.id + ' auto-remediated'

    except ClientError as e:
        print(e)

    return response


```

Environment variable:
![1](/AWS-Security-Workshop/images/gd_1/8-2.PNG)

### Test lambda function:

- Create a testing event used to stimulate a Guarduty finding on order to test the functions response of "UnauthorizedAccess"

```json
{
  "version": "0",
  "id": "cd2d702e-ab31-411b-9344-793ce56b1bc7",
  "detail-type": "GuardDuty Finding",
  "source": "aws.guardduty",
  "account": "<<Account ID>>",
  "time": "1970-01-01T00:00:00Z",
  "region": "us-east-1",
  "resources": [],
  "detail": {
    "schemaVersion": "2.0",
    "accountId": "<<Account ID>>",
    "region": "us-east-1",
    "partition": "aws",
    "id": "b0baa89de4ab301f8d0a8c9a3dfd5726",
    "arn": "arn:aws:guardduty:us-east-1:<<Account ID>>:detector/feb3c048238f682b8902532ec100b3fb/finding/b0baa89de4ab301f8d0a8c9a3dfd5726",
    "type": "UnauthorizedAccess:EC2/TorClient",
    "resource": {
      "instanceDetails": {
        "instanceId": "<<Instance ID>>"
      }
    }
  }
}
```

![1](/AWS-Security-Workshop/images/gd_1/9-testevent.PNG)
![1](/AWS-Security-Workshop/images/gd_1/9.1.PNG)
**CloudWatch logs**

- Lambda has recorded the event an output the nessary information of: -> Instance ID, Describe the instance
- Disable the instance termination
- Prevent the instance from shutting down
- Create tags "isolated"
- Chance the security groups of the instance into "ForensicSG"
- Create a snapshot EBS
  ![1](/AWS-Security-Workshop/images/gd_1/10.PNG)
  ![1](/AWS-Security-Workshop/images/gd_1/10.1.PNG)

**Result**
![1](/AWS-Security-Workshop/images/gd_1/11.PNG)
![1](/AWS-Security-Workshop/images/gd_1/11.1.PNG)
![1](/AWS-Security-Workshop/images/gd_1/11.2.PNG)

### EventBridge Rule

Create event buses rule to trigger lambda when guardduty create a finding of:
Define the custom event pattern with the following content to catch outgoing anonymous (TOR) connections (which usually indicates that there is a malware in the instance trying to contact their Command & Control or Cryptocurrency mining activities):

```json
{
  "source": ["aws.guardduty"],
  "detail": {
    "type": [
      "UnauthorizedAccess:EC2/TorClient",
      "Backdoor:EC2/C&CActivity.B!DNS",
      "Trojan:EC2/DNSDataExfiltration",
      "CryptoCurrency:EC2/BitcoinTool.B",
      "CryptoCurrency:EC2/BitcoinTool.B!DNS"
    ]
  }
}
```

![1](/AWS-Security-Workshop/images/gd_1/12.PNG)
![1](/AWS-Security-Workshop/images/gd_1/12-lambda&eventbr.PNG)
![1](/AWS-Security-Workshop/images/gd_1/12.2.PNG)

### Stimulate attack

1. Get the TestLinux-CryptoMining privateIP (just simply create a new instance of linux which allow ssh within internal network)
   ![1](/AWS-Security-Workshop/images/gd_1/13-test-ec2.PNG)
2. Connect to target TestLinux instance through RedTeam instance call the fake domain that is used to test Command & Control Findings with the following command:

```shell
dig GuardDutyC2ActivityB.com any
```

![1](/AWS-Security-Workshop/images/gd_1/13.1.PNG) 3) Guardduty will create a finging of "Backdoor C&C" event
![1](/AWS-Security-Workshop/images/gd_1/14-res.PNG) 4) Result:
![1](/AWS-Security-Workshop/images/gd_1/14.1.PNG)
![1](/AWS-Security-Workshop/images/gd_1/14.2.PNG)
![1](/AWS-Security-Workshop/images/gd_1/14.3.PNG)

## Step-Functions response
