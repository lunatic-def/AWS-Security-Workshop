---
title: "Autonomous Patching With EC2 Image Builder And Systems Manager"
date: "`r Sys.Date()`"
weight: 5
chapter: false
---

**Main tools in this labs contains:**

- EC2 image builder
- [Systems Manager Automated Document](https://aws.amazon.com/systems-manager/) to orchestrate the execution
- Cloudformation with [AutoScalingReplicingUpdate](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-updatepolicy.html) update policy, to gracefully deploy the newly created AMI into the workload with minimal interruption to the application availability.
- Terraform with [Instance Refresh](https://docs.aws.amazon.com/autoscaling/ec2/userguide/instance-refresh-overview.html) for blue-green deployment (optional)

## Overview

Pathching is a vital component to any security strategy which ensures that your compute environments are operating with the latest code revisions available. This in turn means that you are running with the latest security updates for the system, which reduces the potential attack surface of your workload.

- Automated pathching solution
- Blue/green deployment methology to build an entirely new AMI contains the latest OS patch

1. CloudFormation detects the need to update the LaunchConfiguration with a new Amazon Machine Image.
2. CloudFormation will launch a new AutoScalingGroup, along with the compute resource (EC2 Instance) with the newly patched AMI.
3. CloudFormation will then wait until all instances are detected healthy by the Load balancer, before terminating the old AutoScaling Group, ultimately achieving a blue/green model of deployment.
4. If the new compute resource failed to deploy, cloudformation will rollback and keep the old compute resource running.

### Application infrastructure

![topo](/AWS-Security-Workshop/images/well_4/topo.png)
Cloudformation blue-green update on autoscaling update policy:

[CloudFormation-Updatepolicy](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-updatepolicy.html)

```yaml
UpdatePolicy:
  AutoScalingReplacingUpdate:
    WillReplace: True
```

[Terraform method](https://github.com/orgs/gruntwork-io/discussions/800)

```tf
module "asg_instance_refresh" {

  source = "git::git@github.com:gruntwork-io/terraform-aws-asg.git//modules/asg-instance-refresh?ref=v0.21.15"
...
}
```

To replace the Auto Scaling group and the instances it contains, use the AutoScalingReplacingUpdate policy.

Before attempting an update, ensure that you have sufficient Amazon EC2 capacity for both your old and new Auto Scaling groups.

### AMI Builder pipeline

EC2 Image Builder is a service that simplifies the creation, maintenance, validation, sharing, and deployment of Linux or Windows Server images for use with Amazon EC2 and on-premises. Using this service, eliminates the automation heavy lifting you have to build in order to streamline the build and management of your Amazon Machine Image.

Upon completion of this section we will have an Image builder pipeline that will be responsible for taking a golden AMI Image, and produce a newly patched Amazon Machine Image, ready to be deployed to our application cluster, replacing the outdated one.

**Steps:**

- [Step 1: ](#create-iam-role)
- [Step 2: ](#create-a-security-group)
- [Step 3: ](#create-component)
- [Step 4: ](#create-an-image-builder-recipe)
- [Step 5: ](#create-an-image-builder-pipeline-using-the-recipe)

#### Create IAM role

**SSM service-role**
![2](/AWS-Security-Workshop/images/well_4/2-2.PNG)
Add inline policy:
![2](/AWS-Security-Workshop/images/well_4/2-3.PNG)

#### Create a Security Group

#### Create component

#### Create an Image Builder Recipe

#### Create an Image Builder Pipeline using the Recipe

### Build Automation with SSM

Orchestrate the build of a newly patched AMI and its associated deployment into an application cluster.
![topo](/AWS-Security-Workshop/images/well_4/topo2.png)
To automate this using [AWS SM Automation Document](https://docs.aws.amazon.com/systems-manager/latest/userguide/automation-documents.html)

- Automate the execution of the EC2 Image Builder Pipeline.

```yaml
mainSteps:
    - name: ExecuteImageCreation
    action: aws\:executeAwsApi
    maxAttempts: 10
    timeoutSeconds: 3600
    onFailure: Abort
    inputs:
        Service: imagebuilder #namespace of the service
        Api: StartImagePipelineExecution   #API operation of the imagebuilder
        imagePipelineArn: '{{ ImageBuilderPipelineARN }}'
    outputs:
    - Name: imageBuildVersionArn #output the builder version
        Selector: $.imageBuildVersionArn
        Type: String

```

- Wait for the pipeline to complete the build, and capture the newly created AMI with updated OS patch.
- Once the wait is complete, and the Image is ready -> capture thw AMI Id and pass value to the next step

```yaml
- name: WaitImageComplete
  action: aws:waitForAwsResourceProperty
  maxAttempts: 10
  timeoutSeconds: 3600
  onFailure: Abort
  inputs:
    Service: imagebuilder
    Api: GetImage
    imageBuildVersionArn: "{{ ExecuteImageCreationimageBuildVersionArn }}"
    PropertySelector: image.state.status
    DesiredValues:
      - AVAILABLE
- name: GetBuiltImage
  action: aws:executeAwsApi
  maxAttempts: 10
  timeoutSeconds: 3600
  onFailure: Abort
  inputs:
    Service: imagebuilder
    Api: GetImage
    imageBuildVersionArn: "{{ExecuteImageCreationimageBuildVersionArn }}"
  outputs:
    - Name: image
      Selector: $.image.outputResources.amis[0].image
      Type: String
```

- Then it will Update the CloudFormation application stack with the new patched Amazon Machine Image.
- Wait for the cloudformation to finish updating

```yaml
- name: UpdateCluster
  action: aws:executeAwsApi
  maxAttempts: 10
  timeoutSeconds: 3600
  onFailure: Abort
  inputs:
    Service: cloudformation
    Api: UpdateStack
    StackName: "{{ ApplicationStack }}"
    UsePreviousTemplate: true
    Parameters:
      - ParameterKey: BaselineVpcStack
        UsePreviousValue: true
      - ParameterKey: AmazonMachineImage
        ParameterValue: "{{ GetBuiltImage.image }}"
    Capabilities:
      - CAPABILITY_IAM

- name: WaitDeploymentComplete
  action: aws:waitForAwsResourceProperty
  maxAttempts: 10
  timeoutSeconds: 3600
  onFailure: Abort
  inputs:
    Service: cloudformation
    Api: DescribeStacks
    StackName: "{{ ApplicationStack }}"
    PropertySelector: Stacks[0].StackStatus
    DesiredValues:
      - UPDATE_COMPLETE
```

This AMI update to the stack will in turn trigger the CloudFormation AutoScalingReplacingUpdate policy to perform a simple equivalent of a blue/green deployment of the new Autoscaling group.
