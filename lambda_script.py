import boto3
import os
import json
from datetime import datetime

def expensive_instances_checker(event, context):
    # Get Profiles to inspect multiple AWS accounts,
    # Profiles contains key,value pairs of profile name and path in secrets manager
    profiles = json.loads(os.environ.get('PROFILES'))
    for profile_name in profiles.keys():
        # Get AWS account credentials from secrets manager
        secretsmanager = boto3.client('secretsmanager')
        get_secret_value_response = secretsmanager.get_secret_value(SecretId = profiles[profile_name])
        configs = json.loads(get_secret_value_response['SecretString'])
        
        # Connect to EC2 and RDS service
        ec2 = boto3.client('ec2',
            aws_access_key_id=configs['aws_access_key_id'],
            aws_secret_access_key=configs['aws_secret_access_key'],
            region_name=configs['region'])
        rds = boto3.client('rds',
            aws_access_key_id=configs['aws_access_key_id'],
            aws_secret_access_key=configs['aws_secret_access_key'],
            region_name=configs['region'])
        
        # List down all EC2 & RDS instances
        ec2_instances = ec2.describe_instances()
        rds_instances = rds.describe_db_instances()
        
        # Initialize a list to store the expensive instances
        ec2_expensive_instances = []
        rds_expensive_instances = []
        
        # Get the list of allowed instance types from environment variables
        expensive_ec2_instance_types = os.environ.get('EXPENSIVE_EC2_INSTANCE_TYPES').split(',')
        expensive_rds_instance_types = os.environ.get('EXPENSIVE_RDS_INSTANCE_TYPES').split(',')
        
        # Check if any expensive EC2 instances are running
        for instance in ec2_instances['Reservations']:
            for inst in instance['Instances']:
                if inst['State']['Name'] == 'running' and inst['InstanceType'] in expensive_ec2_instance_types:
                        ec2_expensive_instances.append({
                            'InstanceId': inst['InstanceId'],
                            'InstanceType': inst['InstanceType']
                        })
        
        # Check if any expensive RDS instances are running
        for instance in rds_instances['DBInstances']:
            if instance['DBInstanceClass'] in expensive_rds_instance_types:
                rds_expensive_instances.append({
                    'DBInstanceIdentifier': instance['DBInstanceIdentifier'],
                    'DBInstanceClass': instance['DBInstanceClass']
                })
        
        # If there are expensive instances, send out an SNS notification
        if ec2_expensive_instances or rds_expensive_instances:
            sns = boto3.client('sns')
            sns.publish(
                TopicArn=os.environ.get('SNSTopic'),
                Message=json.dumps({'EC2 expensive_instances': ec2_expensive_instances,
                                'RDS expensive_instances': rds_expensive_instances}),
                Subject='Expensive EC2 and RDS instances found!'
            )

        # Store informaton to S3
        s3 = boto3.client("s3")
        today = datetime.today().strftime("%Y-%m-%d")
        file_name = f"{today}_{profile_name}.json"
    
        # JSON data to write to S3
        s3.put_object(
            Bucket="expensive-instance-logs",
            Key=file_name, 
            Body=json.dumps({'EC2 expensive_instances': ec2_expensive_instances,
                            'RDS expensive_instances': rds_expensive_instances}))

    return {
        'statusCode': 200,
        'body': json.dumps({'EC2 expensive_instances': ec2_expensive_instances,
                            'RDS expensive_instances': rds_expensive_instances})
    }