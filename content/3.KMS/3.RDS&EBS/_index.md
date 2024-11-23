---
title: "RDS(Aurora) - EBS"
date: "`r Sys.Date()`"
weight: 3
chapter: false
---

**TABLE OF CONTENTS**

- [Aurora postgresSQL](/3.kms/3.rdsebsdynamodb/#aurora-postgressql)

- [EBS](/3.kms/3.rdsebsdynamodb/#ebs)

- [DynamoDB](/3.kms/3.rdsebsdynamodb/#dynamodb)

## Aurora (PostgresSQL)

### *Encryption at rest*
Simply enable encryption within the creation process.

{{% notice note %}}
When Encryption is enabled all DB instance volumes, logs, backups, and snapshots are encrypted.

- You **can't unencrypt** an **encrypted DB cluster**. However, you can export data from an encrypted DB cluster and import the data into an unencrypted DB cluster.
- You can't create an **encrypted snapshot** of an **unencrypted DB cluster**.
- A snapshot of _an encrypted DB cluster must be encrypted using the same KMS key as the DB cluster_.
- You can't convert an **unencrypted DB cluster** to an **encrypted one**. However, you can restore an **unencrypted snapshot** to an **encrypted Aurora DB cluster**. To do this, specify a KMS key when you restore from the unencrypted snapshot.
- You can't create an **encrypted Aurora Replica** from an **unencrypted Aurora DB cluster**. You can't create an **unencrypted Aurora Replica** from an **encrypted Aurora DB cluster**.
- To copy an **encrypted snapshot** from one AWS Region to another, you must specify the KMS key in the destination AWS Region. This is because KMS keys are specific to the AWS Region in which they are created. The source snapshot remains encrypted throughout the copy process. Amazon Aurora uses envelope encryption to protect data during the copy process.
  {{% /notice %}}

### *Encryption in transit*
***1) Create custom Aurora PostgreSQL parameter group***

RDS -> Parameter group = *Aurora-postgresql11* as group family -> Type = DB Cluster Parameter Group
GroupName = aurora-pg-ssl -> Create

Parameter group = *Aurora-postgresql11* -> filter and edit *rds.force_ssl=1* -> Save

***2) Connect to DB cluster***

- Allow security group of bastion host or Cloud9
```shell
sudo apt -y install postgresql
```

- Connect to your RDS cluster:

```shell
psql -h CLUSTER_NODE -d workshop -U postgres
```
## EBS
- An encrypted volume which is attached to an EC2 instance supports the following types of encryptions

    * Data at rest inside the volume
    * All data moving between the volume and the instance
    * All snapshots created from the volume
    * All volumes created from those snapshots
### Encrypted volume
1) Create a simple snapshot
```shell
aws ec2 create-snapshot --volume-id YOUR_VOLUME_ID --description "unencrypted workshop snapshot"

```
Output return *SnapshotId*:
```json
{
    "Description": "unencrypted workshop snapshot",
    "Encrypted": false,
    "OwnerId": "913120230671",
    "Progress": "",
    "SnapshotId": "snap-036541022a7b5d1c1",
    "StartTime": "2021-02-15T12:29:59+00:00",
    "State": "pending",
    "VolumeId": "vol-0d5233d220927c599",
    "VolumeSize": 8,
    "Tags": []
}
```

2) Create kms key
```shell
aws kms create-key
```
```json
{
    "KeyMetadata": {
        "AWSAccountId": "ACCOUNT_ID",
        "KeyId": "efd7acd1-ffd8-4cd7-9f97-46e59080074e",
        "Arn": "arn\:aws\:kms\:eu-central-1:ACCOUNT_ID\:key/efd7acd1-ffd8-4cd7-9f97-46e59080074e",
        "CreationDate": "2021-02-15T13:28:11.171000+01:00",
        "Enabled": true,
        "Description": "",
        "KeyUsage": "ENCRYPT_DECRYPT",
        "KeyState": "Enabled",
        "Origin": "AWS_KMS",
        "KeyManager": "CUSTOMER",
        "CustomerMasterKeySpec": "SYMMETRIC_DEFAULT",
        "EncryptionAlgorithms": [
            "SYMMETRIC_DEFAULT"
        ]
    }
}
```
3) Encrypted the snaphot
```shell
aws ec2 copy-snapshot --source-region eu-central-1 --source-snapshot-id YOUR_SNAPSHOT_ID --kms-key-id YOUR_KEY_ID --encrypted --description "encrypted workshop snapshot"
```
4) Create a new volume from the encrypted snapshot
```shell
aws ec2 create-volume --snapshot-id YOUR_SNAPSHOT_ID --availability-zone eu-central-1a
```
5) Attach the volume to the EC2 instance
```shell
aws ec2 attach-volume --instance-id YOUR_INSTANCE_ID --volume-id YOUR_VOLUME_ID --device "/dev/sdf"
```
6) Format and mount the volume and create a file, 

```shell
ssh -i ssh-private-key.pem ec2-user@IP_OF_YOUR_INSTANCE
sudo mkfs -t ext4 /dev/sdf
mkdir data
sudo mount /dev/sdf data
sudo chown -R ec2-user: data/
truncate -s 1G data/foo.txt
ls -l data
```
### Cross-region replication
Share EBS volume in another region - encrypt the transfered EBS with the target region kms key\
```shell
aws ec2 copy-snapshot --source-region eu-central-1 --source-snapshot-id YOUR_ENCRYPTED_SNAPSHOT_IN_EU_CENTRAL_1 --kms-key-id YOUR_KEY_IN_EU_WEST_1 --encrypted --description "encrypted workshop snapshot 2" --destination-region eu-west-1
```
