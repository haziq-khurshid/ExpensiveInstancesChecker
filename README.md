# ExpensiveInstancesChecker
This CloudFormation template is designed to provide a solution for monitoring EC2 and RDS instances in your AWS account and sending out notifications via SNS if any of the running instances are considered "expensive".

## Overview
The solution includes the following AWS resources:

* An EventBridge Trigger to run the Lambda function once on Weekdays.
* A Lambda function that will perform the actual check for expensive instances.
* An IAM role that will be assumed by the Lambda function and grants the necessary permissions for the function to run.
* A Secrets Manager secret that will store the credentials needed to access the EC2 and RDS instances in different profiles.
* An SNS topic which will be used to send out notifications if any expensive instances are detected.
* An SNS subscription to the topic using the email address specified in the NotificationEmail parameter.

## High level Architecture Diagram
![ArchitectureDiagram](https://user-images.githubusercontent.com/55794242/218303749-7d4f043d-4df4-47be-a9bf-eea66150cd0a.png)


## Usage
To use this CloudFormation template, follow these steps:

* Log in to your AWS account.
* In the AWS Management Console, navigate to the CloudFormation service.
* Click on the Create Stack button.
* In the Create Stack page, choose Upload a template file and select the .yml file for this CloudFormation template.
* Fill in the required parameters as described in the section below.
* Click on the Create Stack button to create the stack.


## Parameters
The following parameters are required to use this CloudFormation template:

* EC2InstanceTypes & RDSInstanceTypes: This CloudFormation solution uses environment variables to determine which EC2 and RDS instance types are considered "expensive". To configure these, modify the default parameters in CloudFormation setup or update later in the Lambda function configuration. These variables should be a comma-separated list of instance types.
* NotificationEmail: The email address to receive notifications if any expensive instances are detected. Subscription should also be confirmed from specified email address later.
* Profiles: JSON string of key,value pairs for different aws profiles and secrets manager path where their credentials are stored. Default already given.
* SecretName: The name of the Secrets Manager secret that will store the credentials needed to access the EC2 and RDS instances in different profiles. It should be same as the key given in Profiles variable.
* SecretValue: The JSON string that contains the secrets for the different profiles. An example is provided below:
`{
    "aws_access_key_id": "ACCESS_KEY_ID",
    "aws_secret_access_key": "SECRET_ACCESS_KEY",
    "region": "REGION_NAME"
}`


## Clean-up
To remove the resources created by this CloudFormation template, simply delete the CloudFormation stack from the AWS Management Console.
