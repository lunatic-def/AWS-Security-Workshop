---
title: "Dynamodb-S3-ClientSide(SDK)"
date: "`r Sys.Date()`"
weight: 4
chapter: false
---

**Topics:**

- [DynamoDB](#dynamodb)
- [S3](#s3)
- [SDK - python](#clientside-sdk)

## DynamoDB

When creating a new table, you can choose one of the following KMS keys to encrypt your table:

- **AWS owned KMS key** – Default encryption type. The key is owned by DynamoDB (no additional charge).

- **AWS managed KMS key** – The key is stored in your account and is managed by AWS KMS (AWS KMS charges apply).

- **Customer managed KMS key** – The key is stored in your account and is created, owned, and managed by you. You have full control over the KMS key (AWS KMS charges apply).

DynamoDB encryption at rest provides an additional layer of data protection by securing your data in an encrypted table

- **Encrypted table**
  - Include primary key - local - global secondary indexes - streams - global tables - backups - Dynamodb Accelerator (DAX) clusters
  - Organizational policies, industry or government regulations, and compliance requirements often require the use of encryption at rest to increase the data security.

### Client-side encryption for DynamoDB

**[Introduction Database Encryption](https://docs.aws.amazon.com/database-encryption-sdk/latest/devguide/what-is-database-encryption-sdk.html)**

- **Keyrings:** specify the wrapping-keys that encrypt your data-keys -> use for encrypt and decrypt
- **Encrypting and signing table items:**
  => _item encryptor_ that encrypts, signs, verifies, and decrypts table items

**To encrypt and sign a table item:**

1.  Information about the table
2.  Attributes to encrypt and sign:
    - Encrypt and sign – Encrypt the attribute value. Include the attribute (name and value) in the item signature.
    - Sign only – Include the attribute in the item signature.
    - Do nothing – Do not encrypt or sign the attribute.
3.  Encryption materials, including encryption and signing keys: A cryptographic materials provider (CMP)

        -> collects, assembles, and returns the cryptographic materials that the item encryptor uses to encrypt and sign your table items.

        -> determines the encryption algorithms to use and how to generate and protect encryption and signing keys.

    ![1](/AWS-Security-Workshop/images/kms_3/1.PNG)

**Direct KMS CMP**

- Protects your tavle items under an KMS key
  ![1](/AWS-Security-Workshop/images/kms_3/2.PNG)

```python
#Encrypt table sdk - example
"""Example showing use of AWS KMS CMP with EncryptedTable."""
import boto3
from boto3.dynamodb.types import Binary

from dynamodb_encryption_sdk.encrypted.table import EncryptedTable
from dynamodb_encryption_sdk.identifiers import CryptoAction
from dynamodb_encryption_sdk.material_providers.aws_kms import AwsKmsCryptographicMaterialsProvider
from dynamodb_encryption_sdk.structures import AttributeActions

def encrypt_item(table_name, aws_cmk_id):
    """Demonstrate use of EncryptedTable to transparently encrypt an item."""
    index_key = {"partition_attribute": "is this", "sort_attribute": 55}
    plaintext_item = {
        "example": "data",
        "some numbers": 99,
        "and some binary": Binary(b"\x00\x01\x02"),
        "leave me": "alone",  # We want to ignore this attribute
    }
    # Collect all of the attributes that will be encrypted (used later).
    encrypted_attributes = set(plaintext_item.keys())
    encrypted_attributes.remove("leave me")
    # Collect all of the attributes that will not be encrypted (used later).
    unencrypted_attributes = set(index_key.keys())
    unencrypted_attributes.add("leave me")
    # Add the index pairs to the item.
    plaintext_item.update(index_key)

    # Create a normal table resource.
    table = boto3.resource("dynamodb").Table(table_name)  # generated code confuse pylint: disable=no-member
    # Create a CMP using the specified AWS KMS key.
    aws_kms_cmp = AwsKmsCryptographicMaterialsProvider(key_id=aws_cmk_id)
    # Create attribute actions that tells the encrypted table to encrypt all attributes except one.
    actions = AttributeActions(
        default_action=CryptoAction.ENCRYPT_AND_SIGN, attribute_actions={"leave me": CryptoAction.DO_NOTHING}
    )
    # Use these objects to create an encrypted table resource.
    encrypted_table = EncryptedTable(table=table, materials_provider=aws_kms_cmp, attribute_actions=actions)

    # Put the item to the table, using the encrypted table resource to transparently encrypt it.
    encrypted_table.put_item(Item=plaintext_item)

    # Get the encrypted item using the standard table resource.
    encrypted_item = table.get_item(Key=index_key)["Item"]

    # Get the item using the encrypted table resource, transparently decyrpting it.
    decrypted_item = encrypted_table.get_item(Key=index_key)["Item"]

    # Verify that all of the attributes are different in the encrypted item
    for name in encrypted_attributes:
        assert encrypted_item[name] != plaintext_item[name]
        assert decrypted_item[name] == plaintext_item[name]

    # Verify that all of the attributes that should not be encrypted were not.
    for name in unencrypted_attributes:
        assert decrypted_item[name] == encrypted_item[name] == plaintext_item[name]

    # Clean up the item
    encrypted_table.delete_item(Key=index_key)
```

#### Helper classes

**[Helper Clients - python](https://aws-dynamodb-encryption-python.readthedocs.io/en/latest/lib/encrypted/table.html#module-dynamodb_encryption_sdk.encrypted.table)**

**[TableInfo - represents a DynamoDB table, complete with fields for its primary key and secondary indexes. It helps you to get accurate, real-time information about the table.](https://aws-dynamodb-encryption-python.readthedocs.io/en/latest/lib/tools/structures.html)**

- Mirror the Boto 3 classes for DynamoDB -> designed to make it easier to add encryption and signing to your existing DynamoDB application and avoid the most common problems:
  - Prevent from encrypting the primary key
  - Create a TableInfo object and populate the DynamoDB encryption context based on a call to DynamoDB
  - Support methods, such as put_item and get_item

**Attribute actions in python**

```python
DO_NOTHING = 0
SIGN_ONLY = 1
ENCRYPT_AND_SIGN = 2

"""For example, this AttributeActions object establishes ENCRYPT_AND_SIGN as the default for all attributes, and specifies exceptions for the ISBN and PublicationYear attributes."""


actions = AttributeActions(
    default_action=CryptoAction.ENCRYPT_AND_SIGN,
    attribute_actions={
        'ISBN': CryptoAction.DO_NOTHING,
        'PublicationYear': CryptoAction.SIGN_ONLY
    }
)
```

=> If you use a client helper class, you don't need to specify an attribute action for the primary key attributes. The client helper classes prevent you from encrypting your primary key.

{{% notice warning %}}
Do not encrypt the primary key attributes. They must remain in plaintext so DynamoDB can find the item without running a full table scan.
{{% /notice %}}
{{% notice warning %}}
If you **do not use a client helper class** and the default action is **ENCRYPT_AND_SIGN**, you must specify an action for the primary key. - The recommended action for primary keys is SIGN_ONLY.
{{% /notice %}}
=> To make this easy, use the set_index_keys method, which uses SIGN_ONLY for primary keys, or DO_NOTHING, when that is the default action.

```py
actions = AttributeActions(
    default_action=CryptoAction.ENCRYPT_AND_SIGN,
)
actions.set_index_keys(*table_info.protected_index_keys())
```

#### Example Code

**Topic:**

- [Use the EncryptedTable client helper class](/3.kms/4.s3/#EncryptedTable)
- [Use the item encryptor](https://docs.aws.amazon.com/database-encryption-sdk/latest/devguide/python-examples.html)

How to use the Direct KMS Provider with the _EncryptedTavle_ client helper class:

#### EncryptedTable

- Includes creating the DynamoDB encryption context
- Making sure the primary key attributes are always signed, but never encrypted.

To create the encryption context and discover the primary key, the client helper classes call the DynamoDB DescribeTable operation. To run this code, you must have permission to call this operation.

```python
#1.Create the table
table_name='test-table'
table = boto3.resource('dynamodb').Table(table_name)

#2.Create a CMP
kms_key_id='arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab'
kms_cmp = AwsKmsCryptographicMaterialsProvider(key_id=kms_key_id)

#3.Create the attribute actions object
""" The AttributeActions object in this example encrypts and signs all items except for the test attribute, which is ignored. """
actions = AttributeActions(
    default_action=CryptoAction.ENCRYPT_AND_SIGN,
    attribute_actions={'test': CryptoAction.DO_NOTHING}
)

#4.Create the encrypted table
encrypted_table = EncryptedTable(
    table=table,
    materials_provider=kms_cmp,
    attribute_actions=actions
)
#5.Put the plaintext item in the table
""" When you call the put_item method on the encrypted_table, your table items are transparently encrypted, signed, and added to your DynamoDB table. """
plaintext_item = {
    'partition_attribute': 'value1',
    'sort_attribute': 55
    'example': 'data',
    'numbers': 99,
    'binary': Binary(b'\x00\x01\x02'),
    'test': 'test-value'
}
encrypted_table.put_item(Item=plaintext_item)
```

### Item encryptor

**[link example](https://docs.aws.amazon.com/database-encryption-sdk/latest/devguide/python-examples.html)**

The item encryptor is a lower-level component that performs cryptographic operations for the DynamoDB Encryption Client. It requests cryptographic materials from a cryptographic materials provider (CMP), then uses the materials that the CMP returns to encrypt and sign, or verify and decrypt, your table item.

You can interact with the item encryptor directly or use the helpers that your library provides. For example, the DynamoDB Encryption Client for Java includes an AttributeEncryptor helper class that you can use with the DynamoDBMapper, instead of interacting directly with the DynamoDBEncryptor item encryptor. The Python library includes EncryptedTable, EncryptedClient, and EncryptedResource helper classes that interact with the item encryptor for you.

## S3

There are three different methods to perform server-side encryption, you can choose only one at a time:

- Server-Side Encryption with Amazon S3-Managed Keys (SSE-S3)
- Server-Side Encryption with KMS Keys Stored in AWS Key Management Service (SSE-KMS)
- Server-Side Encryption with Customer-Provided Keys (SSE-C)

**Topics:**

- [SSE-S3](#sse-s3)
- [SSE-KMS](#sse-kms)
- [SSE-C](#sse-c)

### SSE-S3

SSE-S3 is the simplest method to use as encryption keys are handled and managed by AWS. SSE-S3 is based on AES-256 encryption algorithm, a symetric cypher. You cannot access this key or use it manually for any other encryption processing. The key is itself encrypted with a master key that is regularly rotated.

```shell
#create bucker
aws s3 mb s3://bucket-encrypt-sses3-yourname-date
#Enable encryption
aws s3api put-bucket-encryption --bucket bucket-encrypt-sses3-yourname-date  --server-side-encryption-configuration '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'
#Get the current encryption configuration
aws s3api get-bucket-encryption --bucket bucket-encrypt-sses3-yourname-date
```

Output:

```json
{
  "ServerSideEncryptionConfiguration": {
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        },
        "BucketKeyEnabled": false
      }
    ]
  }
}
```

**Force the encryption of uploaded objects:**

The following policy denies permission to upload ab onject unless the request includes the x-amz-server-side-encryption header to request server-side encryption:

```json
{
  "Version": "2012-10-17",
  "Id": "PutObjectPolicy",
  "Statement": [
    {
      "Sid": "DenyIncorrectEncryptionHeader",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::awsexamplebucket1/*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption": "AES256"
        }
      }
    },
    {
      "Sid": "DenyUnencryptedObjectUploads",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::awsexamplebucket1/*",
      "Condition": {
        "Null": {
          "s3:x-amz-server-side-encryption": "true"
        }
      }
    }
  ]
}
```

### SSE-KMS

The main advantage of SSE-KMS over SSE-S3 is the additional level of security provided by permissions on the KMS key itself, allowing you to enable decryption only to authorized users or applications. SSE-KMS also provides an audit trail that shows when a KMS key was used and by whom

```shell
#create bucker
aws s3 mb s3://bucket-encrypt-sses3-yourname-date
#Enable encryption
aws s3api put-bucket-encryption --bucket bucket-encrypt-ssekms-yourname-date --server-side-encryption-configuration '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "aws:kms", "KMSMasterKeyID":"YOUR_KEY_ID"}}]}'
#Get the current encryption configuration
aws s3api get-bucket-encryption --bucket bucket-encrypt-sses3-yourname-date
```

Output:

```json
{
  "ServerSideEncryptionConfiguration": {
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "aws:kms",
          "KMSMasterKeyID": "404d060f-a0aa-4eae-b452-1cc31c905a0f"
        },
        "BucketKeyEnabled": false
      }
    ]
  }
}
```

### SSE-C

- S3 server-side encryption with customer-provided encryption keys (SSE-C)

```shell
aws s3 mb s3://bucket-encrypt-ssec-<name>-<date>
echo "Test SSE-C" > ssec.txt
openssl rand 32 -out ssec.key
aws s3 cp ssec.txt s3://bucket-encrypt-ssec-<name>-<date>/ssec.txt --sse-c AES256 --sse-c-key fileb://ssec.key
aws s3 cp s3://bucket-encrypt-ssec-<name>-<date>/ssec.txt ssec-downloaded.txt --sse-c AES256 --sse-c-key fileb://ssec.key
cat ssec-downloaded.txt
```

## ClientSide-SDK

**[AWS KMS examples using SDK for Python (Boto3)](https://docs.aws.amazon.com/code-library/latest/ug/python_3_kms_code_examples.html)**

Encrypt

```py
class KeyEncrypt:
    def __init__(self, kms_client):
        self.kms_client = kms_client


    def encrypt(self, key_id):
        """
        Encrypts text by using the specified key.

        :param key_id: The ARN or ID of the key to use for encryption.
        :return: The encrypted version of the text.
        """
        text = input("Enter some text to encrypt: ")
        try:
            cipher_text = self.kms_client.encrypt(
                KeyId=key_id, Plaintext=text.encode()
            )["CiphertextBlob"]
        except ClientError as err:
            logger.error(
                "Couldn't encrypt text. Here's why: %s",
                err.response["Error"]["Message"],
            )
        else:
            print(f"Your ciphertext is: {cipher_text}")
            return cipher_text



```

Decrypt:

```py
class KeyEncrypt:
    def __init__(self, kms_client):
        self.kms_client = kms_client


    def decrypt(self, key_id, cipher_text):
        """
        Decrypts text previously encrypted with a key.

        :param key_id: The ARN or ID of the key used to decrypt the data.
        :param cipher_text: The encrypted text to decrypt.
        """
        answer = input("Ready to decrypt your ciphertext (y/n)? ")
        if answer.lower() == "y":
            try:
                text = self.kms_client.decrypt(
                    KeyId=key_id, CiphertextBlob=cipher_text
                )["Plaintext"]
            except ClientError as err:
                logger.error(
                    "Couldn't decrypt your ciphertext. Here's why: %s",
                    err.response["Error"]["Message"],
                )
            else:
                print(f"Your plaintext is {text.decode()}")
        else:
            print("Skipping decryption demo.")



```
