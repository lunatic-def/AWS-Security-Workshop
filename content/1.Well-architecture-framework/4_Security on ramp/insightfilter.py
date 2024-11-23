import cfnresponse
import json, boto3, logging, botocore
def lambda_handler(event, context):
  if event['RequestType'] == 'Delete':
    cfnresponse.send(event, context, cfnresponse.SUCCESS, None, None)
    return

  security_hub_client = boto3.client("securityhub")
  insight_arn = ""
  insight_filters = """{
    "GeneratorId": [
      {
          "Value": "security-control/Account.",
          "Comparison": "PREFIX"
      },
      {
          "Value": "security-control/IAM.",
          "Comparison": "PREFIX"
      },
      {
          "Value": "security-control/SSM.",
          "Comparison": "EQUALS"
      },
      {
          "Value": "security-control/S3.",
          "Comparison": "PREFIX"
      },
      {
          "Value": "security-control/SecretsManager.",
          "Comparison": "PREFIX"
      },
      {
          "Value": "security-control/KMS.2",
          "Comparison": "EQUALS"
      },
      {
          "Value": "security-control/RDS.10",
          "Comparison": "EQUALS"
      },
      {
          "Value": "security-control/RDS.12",
          "Comparison": "EQUALS"
      },
      {
          "Value": "security-control/ECS.8",
          "Comparison": "EQUALS"
      },
      {
          "Value": "security-control/ECR.1",
          "Comparison": "EQUALS"
      },
      {
          "Value": "security-control/EC2.2",
          "Comparison": "EQUALS"
      },
      {
          "Value": "security-control/EC2.18",
          "Comparison": "EQUALS"
      },
      {
          "Value": "security-control/EC2.19",
          "Comparison": "EQUALS"
      },
      {
          "Value": "security-control/EC2.21",
          "Comparison": "EQUALS"
      },{
          "Value": "security-control/EC2.29",
          "Comparison": "EQUALS"
      },
      {
          "Value": "security-control/RDS.18",
          "Comparison": "EQUALS"
      },
      {
          "Value": "security-control/WAF.10",
          "Comparison": "EQUALS"
      },
      {
          "Value": "security-control/CloudFront.2",
          "Comparison": "EQUALS"
      },
      {
          "Value": "security-control/CloudTrail.3",
          "Comparison": "EQUALS"
      },
      {
          "Value": "security-control/GuardDuty.1",
          "Comparison": "EQUALS"
      }
    ],
    "WorkflowStatus":[
      {"Value":"SUPPRESSED","Comparison":"NOT_EQUALS"},
      {"Value":"RESOLVED","Comparison":"NOT_EQUALS"}
    ],
    "RecordState":[{"Value":"ACTIVE","Comparison":"EQUALS"}]
  }"""
  get_insights_output = security_hub_client.get_insights()
  
  get_insights_data = get_insights_output["Insights"]
  
  for insight in get_insights_data:
    if insight["Name"] == "Security Onramp Posture":
      insight_arn = insight["InsightArn"]
      break

  try:
    if insight_arn == "":
      response = security_hub_client.create_insight(
        Name="Security Onramp Posture",
        GroupByAttribute="SeverityLabel",
        Filters=json.loads(insight_filters))
    else:
      response = security_hub_client.update_insight(
        InsightArn=insight_arn,
        Name="Security Onramp Posture",
        GroupByAttribute="SeverityLabel",
        Filters=json.loads(insight_filters))
  except botocore.exceptions.ClientError as err:
    responseErr = {"Error": "Insight update failed"}
    cfnresponse.send(event, context, cfnresponse.FAILED, responseErr, '')
    raise err
    return
  
  cfnresponse.send(event, context, cfnresponse.SUCCESS, response, None)
  
  return
