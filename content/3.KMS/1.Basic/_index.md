---
title: "Basic commands"
date: "`r Sys.Date()`"
weight: 1
chapter: false
---

SYMMETRIC KEY EXAMPLE:

**_1) list existing keys:_**

```shell
aws kms list-keys
```

Example output:

```json
{
  "Keys": [
    {
      "KeyId": "4ab85425-3ede-4dd1-9f17-914a7e2f33d7",
      "KeyArn": "arn:aws:kms:ap-southeast-2:user_id:key/4ab85425-3ede-4dd1-9f17-XXXXXXXXXXX"
    },
    {
      "KeyId": "69763c19-e28d-44cc-8104-701ae2b42305",
      "KeyArn": "arn:aws:kms:ap-southeast-2:user_id:key/69763c19-e28d-44cc-8104-XXXXXXXXXXX"
    }
  ]
}
```

**_2) Creating a KMS key_**

```shell
aws kms create-key --description "Creating an encryption KMS key"
```

Important "KeyID" for later use:

```json
{
    "KeyMetadata": {
        ...
        "KeyId": "bca1a73c-b9d2-43e2-97e7-XXXXXXXXXXXX",
        ...
    }
}
```

Key alias:

```shell
KEY_ID=YOUR_KEY_ID

aws kms create-alias --target-key-id ${KEY_ID} --alias-name alias/my-kms

```

Key policies:
```shell
aws kms list-key-policies --key-id YOUR_KEY_ID
```

**_3) Generating a Data key_**

- The key for encrypt and decrypt data

```shell
aws kms generate-data-key --key-id alias/my-kms --key-spec AES_256
```

Output:

```json
{
  "CiphertextBlob": "AQIDAHiNuXXnu8SiDat5B2+53PrUzQvrztxy2goKhceTVwNoDAFboLcM9DYLJRprvSF16VWhAAAAfjB8BgkqhkiG9w0BBwagbzBtAgEAMGgGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQMaAKf1DtSn99SoSYsAgEQgDsPACB1itRaJX6yTjEQuWidGXpMYwL9x47oxbepRkjQjIta4jdisEZU3VbqJhGRKLJzwFepzU+ofZWKBA==",
  "Plaintext": "tJ6HM0yWt2SwkEGDhG7IgVilYlU8j2IaX+wrr24Af7w=",
  "KeyId": "arn:aws:kms:ap-southeast-2:user_id:key/0265a04d-b823-4a16-9fbe-772a5cb6baea"
}
```

- CiphertextBlob: the data key store persistently in forder to decrypt and encrypt in future

{{% notice note %}}
While we are using a symmetric key here, we can also trivially do envelope encryption with asymmetric (public/private) keys. In this case, we'd treat the private key as the data key, and use KMS to encrypt it; there is no need to encrypt the public key.
{{% /notice %}}

Store the encrypted version of the Data-key:

```shell
export DATA_KEY_CIPHERTEXT="AQIDAHiNuXXnu8SiDat5B2+53PrUzQvrztxy2goKhceTVwNoDAFboLcM9DYLJRprvSF16VWhAAAAfjB8BgkqhkiG9w0BBwagbzBtAgEAMGgGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQMaAKf1DtSn99SoSYsAgEQgDsPACB1itRaJX6yTjEQuWidGXpMYwL9x47oxbepRkjQjIta4jdisEZU3VbqJhGRKLJzwFepzU+ofZWKBA=="
echo $DATA_KEY_CIPHERTEXT | base64 --decode > data_key_ciphertext
```

**_4) Decrypting Data-key_**

- Need to obtain the plain text -> before using the Data-key.

```shell
export DATA_KEY_PLAINTEXT=`aws kms decrypt --ciphertext-blob fileb://./data_key_ciphertext --query Plaintext --output text`
```

**_5) Encrypting with Data-key_**

- Use the plaintext Data-key to encrypt some content

```shell
echo "$DATA_KEY_PLAINTEXT" | base64 --decode > ./data-key-plaintext
echo "Hello! this is the plain message."  | openssl enc -e -aes256 -k file://./data-key-plaintext > ./ciphertext
cat ./ciphertext
```

```data
Salted__k:^*******
```

**_6) Decrypting with Data-key_**

- Use the plaintext Data-key to decrypt some content

```shell
cat ./ciphertext | openssl enc -d -aes256 -k file://./data-key-plaintext
```

```data
Hello! this is the plain message.
```

**_7) Clean up_**

- Delete the alias of the KMS key

```cmd
aws kms delete-alias --alias-name alias/my-kms
```

- Schedule deletion in 7 days for KMS key

```cmd
aws kms schedule-key-deletion --key KEY_ID --pending-window-in-days 7
```
