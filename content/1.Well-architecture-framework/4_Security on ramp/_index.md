---
title: "Automate assessment security best practice"
date: "`r Sys.Date()`"
weight: 4
chapter: false
---

**Main tools in this labs contains:**

- Well architected framework
- AWS Trusted advisor
- AWS Config
- AWS Security Hub
- AWS Well-architected tools

## Parts

- **[Overview](#overview)**
- **[Automated assessment with AWS Config, AWS Security Hub](#automated-assessment)**
- **[Manial assessment with AWS Well-archtected tool](#manual-assessment)**
- **[AWS trusted advisor overview](#aws-trusted-advisor)**

### Overview

The following controls are included in the assessment => 8 foundational best practices to assess the security posture

**SO 1. Accurate Account Information**

1. Accurate account information helps AWS account teams identify primary and alternate contacts in your business. With correct information, your account team can reach out to you and open a channel of communication with you.
2. In the event of loss of MFA, the account email address and the phone number can be used to authenticate and access your AWS account via the account root user.
3. AWS Security, AWS Trust and Safety, or AWS service teams contact you to inform you of security issues or potential abusive or fraudulent activities on your AWS account.
4. Alternate contacts enable AWS to contact another person about issues with your account, even if the primary account holder is unavailable.

**SO 2. Human Access Control**

1. Multi-factor Authentication (MFA):
   - Ensure MFA is enabled and updated for the primary account. When you enable MFA for the root user, it affects only the root user credentials.
   - Ensure MFS is enabled and update for the IAM users. IAM users in the account are distinct identities with their own credentials, and each identity has its own MFA configuration.
2. Least privilege access:
   - Ensure non-root users are created based on the purpose of the teams/individuals. Instead of in-line policies and permissions use groups to associate permissions for IAM users. Use IAM - Access Analyzer to refine access and build least privilege access with IAM policies.
   - Ensure you use a **centralized identity provider** to store identities and federate access into AWS account(s). Managing IAM users at scale can become complex as the number of users and AWS accounts increases in your cloud environment. For workforce identities, rely on an identity provider that enables you to manage identities in a centralized place. This makes it easier to manage access across multiple applications and services, because you are creating, managing, and revoking access from a single location.
3. Pasword management:
   - If you use IAM users, ensure a password policy is configured through IAM that is not the default password policy for the account.
   - Ensure that you configure password lifecycle by setting a password expiry.
   - If you use federated access to AWS accounts through a centralised identity provider, ensure that a password rotation policy is configured along with a password complexity policy.

**SO 3. Programmatic Access Control**

1. **Ensure no API keys exist for the root user**. As per best practice, **remove all access keys associated with the root user**. The root user has full access to all your resources for all AWS services, including your billing information. You cannot restrict the permissions associated with the root user with IAM permissions.
2. **Ensure access keys are short-lived**(rotated on a schedule) or temporary using AWS Secure Token Service (AWS STS).
3. **Ensure IAM roles are used for instances, containers and serverless functions** to provision temporary access.
4. **Ensure that applications that need to access AWS resources** use AWS SDK and the AWS STS to **generate temporary credentials** in the application cod

**SO 4. Secrets Management**

A secret can be a password, a set of credentials such as a user name and password, an OAuth token, or other secret information

1. **Ensure secrets are rotated on a schedule**. As a best practice, secrets should be short lived. If you don't change your secrets for a long period of time, the secrets become more likely to be mis-used.
2. **Ensure secrets are stored in an encrypted store**. Encryption helps protect data at rest. Some secrets such as integration and access keys for third party tools that cannot be rotated easily should at the least be stored in an encrypted store.
3. **Ensure least privilege and access control to manage how secrets are access and by whom.**
4. **Ensure no secrets are embedded in application code or stored in plain text.**

**SO 5. Network Access Control**

1. Ensure that the default VPC is not being used and you create a custom VPC with at least one public and one private subnet. Using resilience best practices, ensure VPCs are spread across multiple availability zones.
2. Ensure security groups control traffic to and from the resources in the VPC. You can enhance the security configuration of the VPC by using network access control lists (NACLs) at the subnet level.

**Remote access configuration**
Resources like databases and instances can be remotely accessed via the network layer. You have control of your instances, including the kind of traffic that can reach your instance. For example, you can allow computers from only your corporate network to access your instances.

1. **Ensure remote access to instances secured through least privilege**. Remote access should only be needed through privilege escalation when needed.
2. **Ensure interactive remote access configured using AWS Systems Manager Sessions Manager and IAM policies.** Session Manager removes the need to open inbound ports, manage SSH keys, or use jump hosts.
3. In case it is not possible to use Sessions Manager, ensure remote access ports are open only to a restricted IP range such as corporate network or home network.
4. **Ensure edge protection is configured with a web application firewall (WAF) for public facing endpoints.** A web application firewall helps protect your web applications or APIs against common web exploits and bots that may affect availability, compromise security, or consume excessive resources.

**SO 6. Patch Management**

1. **Ensure vulnerability management lifecycle is configured and in use.** Only scanning for vulnerabilities means nothing if appropriate steps are not taken to patch them.
2. **Ensure automated scanning and patching is configured**. Use **Amazon Inspector to automatically scan and detect vulnerabilities in EC2 instances**, container images stored in Amazon Elastic Container Registry (Amazon ECR) and AWS Lambda functions. **AWS Systems Manager Patch Manager can be used to configure maintenance windows and patching.**

**SO 7. S3 Bucket Protection**

**References**

- [AWS Security Blog (Amazon CloudFront introduces Origin Access Control (OAC))](https://aws.amazon.com/blogs/networking-and-content-delivery/amazon-cloudfront-introduces-origin-access-control-oac/)
- [AWS Security Blog (Amazon S3 Encrypts New Objects By Default)](https://aws.amazon.com/blogs/aws/amazon-s3-encrypts-new-objects-by-default/)
- [Amazon Simple Storage Service (S3) (Using bucket policies)](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-policies.html)
- [AWS Samples (Amazon CloudFront Secure Static Website)](https://github.com/aws-samples/amazon-cloudfront-secure-static-site)

1. _Ensure S3 Block Public Access is enabled at an account level._ Customers should enable this setting to make sure that **no S3 buckets in the account can be made public by mistake.** If there is a use case for a bucket to be public like static web hosting, it is good practice to use account level isolation and have a separate account for public assets where the setting can be disabled.
2. **Ensure bucket policies are used for access control**. S3 buckets support resource based policies. Use bucket policies in addition to IAM permissions to build granular access control for data.
3. **For public buckets used for static web hosting, ensure you use Amazon CloudFront with Origin Access Control (OAC).** OAC is based on an AWS best practice of using IAM service principals to authenticate with S3 origins.
4. **Ensure origin security is configured with Amazon CloudFront to protect communication between Amazon CloudFront and your origin server.** It includes enforcing HTTPS-only connection between CloudFront and your origin web-server, supporting for TLSv1.1 and TLSv1.2 between CloudFront and your origin web-server, and adding or modifying request headers forwarded from CloudFront to your origin.
   **SO 8. Baseline Detective Control**

- Ensure AWS CloudTrail is enabled and logging Management Events. Visibility into your AWS account activity is a key aspect of security and operational best practices. You can use CloudTrail to view, search, download, archive, analyze, and respond to account activity across your AWS infrastructure. You can identify who or what took which action, what resources were acted upon, when the event occurred, and other details to help you analyze and respond to activity in your AWS account. The first trail capturing management events is free of cost.
- Ensure Amazon GuardDuty is enabled. Amazon GuardDuty is a security monitoring service that analyzes and processes data sources, such as AWS CloudTrail data events for Amazon S3 logs, CloudTrail management event logs, DNS logs, Amazon EBS volume data, Kubernetes audit logs, Amazon VPC flow logs, and RDS login activity. It uses threat intelligence feeds, such as lists of malicious IP addresses and domains, and machine learning to identify unexpected, potentially unauthorized, and malicious activity within your AWS environment.
- Ensure AWS Cost Anomaly Detection is enabled and configured for your accounts. AWS Cost Anomaly Detection leverages advanced Machine Learning technologies to identify anomalous spend and root causes, so you can quickly take action. It helps you detect and alert on any abnormal or sudden spend increases in your AWS account. This is possible by using machine learning to understand your spend patterns and trigger alert as they seem abnormal.
- Amazon CloudWatch Billing Alarm is configured. You can monitor your estimated AWS charges by using Amazon CloudWatch. When you enable the monitoring of estimated charges for your AWS account, the estimated charges are calculated and sent several times daily to CloudWatch as metric data.

### Automated assessment

![topo1](/AWS-Security-Workshop/images/on-ram1/topo1.png)

1. Security hub collect checks from AWS config compliant assessment example:
   ![1](/AWS-Security-Workshop/images/on-ram1/1-5.PNG)
   ![1](/AWS-Security-Workshop/images/on-ram1/1-6.PNG)
   ![1](/AWS-Security-Workshop/images/on-ram1/1-7.PNG)

AWS Security hub findings using the benchmark enabled:

- CIS AWS Foundation benchmark
- Foundational security best practices
  ![1](/AWS-Security-Workshop/images/on-ram1/1-8.PNG)
  ![1](/AWS-Security-Workshop/images/on-ram1/1-2.PNG)

2. Custom-insight:

**Mechanism**

```
SO 1. Accurate Account Information
AWS Security Hub Checks:

[Account.1] Security contact information should be provided for an AWS account
[Account.2] AWS accounts should be part of an AWS Organizations organization


[IAM.1] IAM policies should not allow full "*" administrative privileges
[IAM.2] IAM users should not have IAM policies attached
[IAM.3] IAM users' access keys should be rotated every 90 days or less
[IAM.4] IAM root user access key should not exist
[IAM.5] MFA should be enabled for all IAM users that have a console password
[IAM.6] Hardware MFA should be enabled for the root user
[IAM.7] Password policies for IAM users should have strong configurations
[IAM.8] Unused IAM user credentials should be removed
[IAM.9] Virtual MFA should be enabled for the root user
[IAM.10] - [IAM.17] Password policies for IAM users should have strong AWS Configurations
[IAM.19] MFA should be enabled for all IAM users
[IAM.20] Avoid the use of the root user
[IAM.21] IAM customer managed policies that you create should not allow wildcard actions for services
[IAM.22] IAM user credentials unused for 45 days should be removed
[KMS.2] IAM principals should not have IAM inline policies that allow decryption and re-encryption actions on all KMS keys

[IAM.1] IAM policies should not allow full "*" administrative privileges
[IAM.2] IAM users should not have IAM policies attached
[IAM.3] IAM users' access keys should be rotated every 90 days or less
[IAM.8] Unused IAM user credentials should be removed
[IAM.21] IAM customer managed policies that you create should not allow wildcard actions for services
[KMS.2] IAM principals should not have IAM inline policies that allow decryption and re-encryption actions on all KMS keys
[RDS.10] IAM authentication should be configured for RDS instances
[RDS.12] IAM authentication should be configured for RDS clusters

[ECS.8] Secrets should not be passed as container environment variables
[SecretsManager.1] Secrets Manager secrets should have automatic rotation enabled
[SecretsManager.2] Secrets Manager secrets configured with automatic rotation should rotate successfully
[SecretsManager.3] Remove unused Secrets Manager secrets
[SecretsManager.4] Secrets Manager secrets should be rotated within a specified number of days


[EC2.2] The VPC default security group should not allow inbound and outbound traffic
[EC2.18] Security groups should only allow unrestricted incoming traffic for authorized ports
[EC2.19] Security groups should not allow unrestricted access to ports with high risk
[EC2.21] Network ACLs should not allow ingress from 0.0.0.0/0 to port 22 or port 3389
[EC2.29] EC2 instances should be launched in a VPC
[RDS.18] RDS instances should be deployed in a VPC
[WAF.10] A WAFV2 web ACL should have at least one rule or rule group


[ECR.1] ECR private repositories should have image scanning configured
[SSM.1] EC2 instances should be managed by AWS Systems Manager
[SSM.2] All EC2 instances managed by Systems Manager should be compliant with patching requirements
[SSM.3] Instances managed by Systems Manager should have an association compliance status of COMPLIANT
[SSM.4] SSM documents should not be public

[CloudFront.2] CloudFront distributions should have origin access identity enabled
[S3.1] S3 Block Public Access setting should be enabled
[S3.2] S3 buckets should prohibit public read access
[S3.3] S3 buckets should prohibit public write access
[S3.4] S3 buckets should have server-side encryption enabled
[S3.5] S3 buckets should require requests to use Secure Socket Layer
[S3.6] Amazon S3 permissions granted to other AWS accounts in bucket policies should be restricted
[S3.8] S3 Block Public Access setting should be enabled at the bucket level
[S3.9] S3 bucket server access logging should be enabled
[S3.10] S3 buckets with versioning enabled should have lifecycle policies configured
[S3.11] S3 buckets should have event notifications enabled
[S3.12] S3 access control lists (ACLs) should not be used to manage user access to buckets
[S3.13] S3 buckets should have lifecycle policies configured
[S3.14] S3 buckets should use versioning
[S3.15] S3 buckets should be configured to use Object Lock
SO 8. Baseline Detective Controls
AWS Security Hub Checks:

[CloudTrail.3] CloudTrail should be enabled
[GuardDuty.1] GuardDuty should be enabled
[IAM.18] Ensure a support role has been created to manage incidents with AWS Support
```

**lambda function filter base on Security hub controls:**
![1](/AWS-Security-Workshop/images/on-ram1/1-9.PNG)
**[Lambda function file]()**

![1](/AWS-Security-Workshop/images/on-ram1/1-4.PNG)
Remediation link for guide on how to fix issues:
![1](/AWS-Security-Workshop/images/on-ram1/res1.PNG)

### Manual assessment
![2](/AWS-Security-Workshop/images/on-ram1/topo2.png)

For the manual assessment -> AWS Well architected tools
- Custom lens (can be shared between accounts)

[FILE LINK]()
```json
{
        "id": "SO_3",
        "name": "SO 3. Programmatic Access Control",
        "questions": [
        {
            "id": "so_3_1",
            "title": "Are access keys for the root user in use?",
            "description": "Access keys are long-term credentials for an IAM user or the AWS account root user. You can use access keys to sign programmatic requests to the AWS CLI or AWS API (directly or using the AWS SDK). Access keys consist of two parts: an access key ID (for example, AKIAIOSFODNN7EXAMPLE) and a secret access key (for example, wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY). Like a user name and password, you must use both the access key ID and secret access key together to authenticate your requests. Manage your access keys as securely as you do your user name and password.",
            "helpfulResource": {
                "displayText": "As a best practice, do not use root user access keys. The access key for your AWS account root user gives full access to all your resources for all AWS services, including your billing information. You cannot reduce the permissions associated with your AWS account root user access key.",
                "url": "https://docs.aws.amazon.com/general/latest/gr/aws-access-keys-best-practices.html"
            },
            "choices": [

            {
                "id": "so_3_1_1",
                "title": "Access keys are not created for the root user.",
                "helpfulResource":{
					"displayText": "Lock away AWS account root user access keys.",
					"url": "https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#lock-away-credentials"
                },
                "improvementPlan": {
					"displayText": "As per best practice, remove all access keys associated with the root user. The access key for your AWS account gives full access to all your resources for all AWS services, including your billing information. You cannot restrict the permissions associated with your AWS account access key.",
					"url": "https://catalog.us-east-1.prod.workshops.aws/workshops/f21a1ec6-e7bc-482c-a6fc-9f53d28f8ac7/en-US/foundational-controls/3-protectrootuser#delete-root-account-access-keys"
                }
            },{
                "id": "so_3_1_no",
				"title": "None of these"
            }],
            
            "riskRules": [{
                "condition": "so_3_1_1",
                "risk": "NO_RISK"
            }, {
                "condition": "default",
                "risk": "HIGH_RISK"
            }]
        },
        ...
    },
```

**Create custom lens:**
![2](/AWS-Security-Workshop/images/on-ram1/2.PNG)
**Pulish the lens**
![2](/AWS-Security-Workshop/images/on-ram1/2-1.PNG)
**Define the workload:**
![2](/AWS-Security-Workshop/images/on-ram1/2-2.PNG)
![2](/AWS-Security-Workshop/images/on-ram1/2-3.PNG)
**Scaning result:**
![2](/AWS-Security-Workshop/images/on-ram1/2-4.PNG)
![2](/AWS-Security-Workshop/images/on-ram1/2-6.PNG)
![2](/AWS-Security-Workshop/images/on-ram1/2-5.PNG)
### AWS trusted advisor
![2](/AWS-Security-Workshop/images/on-ram1/topo3.png)

If you have a Basic Support and Developer Support plan, you can use the Trusted Advisor console to access all checks in the Service limits  category and a subset of checks in the security category:

**Amazon EBS Public Snapshots**

Checks the permission settings for your Amazon Elastic Block Store (Amazon EBS) volume snapshots and alerts you if any snapshots are marked as public. Results for this check are automatically refreshed several times daily, and refresh requests are not allowed. It might take a few hours for changes to appear.

When you make a snapshot public, you give all AWS accounts and users access to all the data on the snapshot. This can lead to considerable loss of data depending on the sensitivity of data stored in the snapshot. Unless you are certain you want to share all the data in the snapshot with all AWS accounts and users, modify the permissions: mark the snapshot as private, and then specify the accounts that you want to give permissions to.

To modify permissions for your snapshots directly, you can use the AWSSupport-ModifyEBSSnapshotPermission  runbook in the AWS Systems Manager console .

**Amazon RDS Public Snapshots** 

Checks the permission settings for your Amazon Relational Database Service (Amazon RDS) DB snapshots and alerts you if any snapshots are marked as public. Results for this check are automatically refreshed several times daily, and refresh requests are not allowed. It might take a few hours for changes to appear.

When you make a snapshot public, you give all AWS accounts and users access to all the data on the snapshot. Unless you are certain you want to share all the data in the snapshot with all AWS accounts and users, modify the permissions: mark the snapshot as private, and then specify the accounts that you want to give permissions to.

To modify permissions for your snapshots directly, you can use the AWSSupport-ModifyRDSSnapshotPermission  runbook in the AWS Systems Manager console .

**Amazon S3 Bucket Permissions**

Checks buckets in Amazon Simple Storage Service (Amazon S3) that have open access permissions, or that allow access to any authenticated AWS user.

This check examines explicit bucket permissions, as well as bucket policies that might override those permissions. Granting list access permissions to all users for an Amazon S3 bucket is not recommended. These permissions can lead to unintended users listing objects in the bucket at high frequency, which can result in higher than expected charges. Permissions that grant upload and delete access to everyone can lead to security vulnerabilities in your bucket.

If a bucket allows open access, determine if open access is truly needed. If not, update the bucket permissions to restrict access to the owner or specific users. Use Amazon S3 Block Public Access to control the settings that allow public access to your data.

**IAM Use**

Checks for the use of IAM. This check is intended to discourage the use of root access by checking for existence of at least one IAM user. You can ignore the alert if you are following best practice of centralizing identities and configuring users in an external identity provider  or AWS IAM Identity Center (successor to AWS Single Sign-On) .

Create an IAM user or use AWS IAM Identity Center (successor to AWS Single Sign-On) to create additional users whose permissions are limited to perform specific tasks in your AWS environment.

**MFA on Root Account**

Checks the root account and warns if multi-factor authentication (MFA) is not enabled.

For increased security, we recommend that you protect your account by using MFA, which requires a user to enter a unique authentication code from their MFA hardware or virtual device when interacting with the AWS Management Console and associated websites.

**Security Groups – Specific Ports Unrestricted** 

Checks security groups for rules that allow unrestricted access (0.0.0.0/0) to specific ports.

Unrestricted access increases opportunities for third-party activities leading to security events (hacking, denial-of-service, loss of data). This check evaluates security groups that you create and their inbound rules for IPv4 addresses. The ports with highest risk are flagged red, and those with less risk are flagged yellow. Ports flagged green are typically used by applications that require unrestricted access, such as HTTP and SMTP. Restrict access to only those IP addresses that require it. To restrict access to a specific IP address, set the suffix to /32 (for example, 192.0.2.10/32). Ensure you delete overly permissive rules after creating rules that are more restrictive.

If you have intentionally configured your security groups in this manner, use additional security measures to secure your infrastructure (such as IP tables).
