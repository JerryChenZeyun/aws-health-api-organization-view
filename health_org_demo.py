####################################################################################################################################################################################
# Script Function: Demonstrate AWS Health API for Organization View
# Author: JC
# Time: 2020.03.08
# Version: 1.0
# Execution requirements: 
#   1. Update the "accountId" value following the instruction from Step 10 in  https://github.com/JerryChenZeyun/aws-health-api-organization-view/blob/master/README.md#setup
#   2. Update the "bucketName" value following the instruction from Step 10 in  https://github.com/JerryChenZeyun/aws-health-api-organization-view/blob/master/README.md#setup
####################################################################################################################################################################################

import boto3
import logging
from botocore.exceptions import ClientError
import json
import datetime
import pandas as pd
import os

####################################################################################################################################################################################
bucketName = 'my-test-bucket-20191011'
####################################################################################################################################################################################

arn_list = []
service_list = []
eventTypeCode_list = []
eventTypeCategory_list = []
region_list = []
startTime_list = []
endTime_list = []
lastUpdatedTime_list = []
statusCode_list = []

# Transform dict format into list format
def dict_to_list():
    client = boto3.client('health')
    event_data = client.describe_events_for_organization(
        filter={
        }
    )
    for i in range(0,len(event_data["events"])):
        arn_list.append(event_data["events"][i]["arn"])
        service_list.append(event_data["events"][i]["service"])
        eventTypeCode_list.append(event_data["events"][i]["eventTypeCode"])
        eventTypeCategory_list.append(event_data["events"][i]["eventTypeCategory"])
        region_list.append(event_data["events"][i]["region"])
        startTime_list.append(event_data["events"][i]["startTime"])
        endTime_list.append(event_data["events"][i]["endTime"])
        lastUpdatedTime_list.append(event_data["events"][i]["lastUpdatedTime"])
        statusCode_list.append(event_data["events"][i]["statusCode"])

## Wraping up the dict info into json message 
def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

## Upload the organization events json message to S3 file
def upload_to_s3(file_name, bucket, key):
    """Upload a file to an S3 bucket
    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """    
    s3 = boto3.resource('s3')        
    try:
        s3.meta.client.upload_file(file_name, bucket, key)
        print("s3 upload success")
    except ClientError as e:
        logging.error(e)
        return False
        print("s3 upload error occurs", e)
    return True
    
csvFileName = 'event_data_file.csv'

# Store event data info into csv file
def write_to_csv():
    whole_table = pd.DataFrame(
        {
            'arn': arn_list,
            'service': service_list,
            'eventTypeCode': eventTypeCode_list,
            'eventTypeCategory': eventTypeCategory_list,
            'region': region_list,
            'startTime': startTime_list,
            'endTime': endTime_list,
            'lastUpdatedTime': lastUpdatedTime_list,
            'statusCode': statusCode_list
        }
    )
    event_data_file = open(csvFileName, "w")
    event_data_file.write(whole_table.to_csv(index = False))
    event_data_file.close()
    print("\n#########################################################################\n")
    print("Event data saved to CSV file.")
    print("\n#########################################################################\n")

## Create the Manifest file, and save it to the user specified S3 bucket
def create_manifest():
    """Create a Manifest file to an user specified S3 bucket
    This is required when user need to visualise the event data hosted in S3 bucket via QuickSight
    """
    dirpath = os.getcwd()
    file_path_ori = dirpath + "/manifest.json"
    file_path_new = dirpath + "/manifests3.json"

    with open(file_path_ori, "rt") as fin:
        with open(file_path_new, "wt") as fout:
            for line in fin:
                fout.write(line.replace('bucket-name', bucketName))

## Enable the health service in organization level
def enable_health_org():
    client = boto3.client('health')
    try:
        response = client.enable_health_service_access_for_organization()
        print("enable health api at organization level success")
    except ClientError as e:
        logging.error(e)
        print("enable health api at organization level error occurs:", e)
    
    print("\n#########################################################################\n")
    print(response)
    print("\n#########################################################################\n")
    print("Health Service has been enabled at AWS Organization Level -- Done!")
    print("\n#########################################################################\n")

## describe_health_service_status_for_organization
def describe_health_service_status_for_org():
    client = boto3.client('health')
    response = client.describe_health_service_status_for_organization()
    print(response)
    print("\n#########################################################################\n")

## describe_events_for_organization(**kwargs)
def describe_events_for_org():
    client = boto3.client('health')
    response_org_event = client.describe_events_for_organization(
        filter={
        }
    )
    print("\n#########################################################################\n")
    print("describe_events_for_organization response is \n")
    print("\n#########################################################################\n")
    print(response_org_event)

## describe_affected_accounts
def describe_affected_accounts():
    client = boto3.client('health')
    ## iterate the event list to retrieve affected account info for each health event
    print("\n#########################################################################\n")
    ## retrieve health event data
    response = client.describe_events_for_organization(
        filter={
        }
    )
    event_arn_list = []
    for i in range(0,len(response["events"])):
        event_arn_list.append(response["events"][i]["arn"])
        print("\n---------------------------------------------------------------------\n")
        print("affected accounts for health event: " + event_arn_list[i])
        response_account = client.describe_affected_accounts_for_organization(eventArn = event_arn_list[i])
        print(response_account)
    print("\n#########################################################################\n")

## Retrieve account id automatically
## NOT in use for this Lab
def get_account_id():
    return(boto3.client('sts').get_caller_identity().get('Account'))

## describe_events_details_for_organization(**kwargs) 
## NOT in use for this Lab
def describe_affected_event_details(event_arn):
    client = boto3.client('health')
    response = client.describe_event_details_for_organization(
        organizationEventDetailFilters=[
            {
                'eventArn': event_arn,
                'awsAccountId': accountId
            },
        ]
    )
    print("\n#########################################################################\n")
    print("Destribe event details for specific account in organization \n")
    print(response)
    print("\n#########################################################################\n")

## describe_affected_entities_for_organization(**kwargs)
## NOT in use for this Lab
def describe_affected_entities(event_arn):
    client = boto3.client('health')
    response = client.describe_affected_entities_for_organization(
        organizationEntityFilters=[
            {
                'eventArn': event_arn,
                'awsAccountId': accountId
            },
        ],
    )
    print("\n#########################################################################\n")
    print("Destribe affected entities for specific account in organization \n")
    print(response)
    print("\n#########################################################################\n")



# Main part of Script
# -------------------
if __name__ == "__main__":  

    client = boto3.client('health')

    ## Enable the health service in organization level
    enable_health_org()

    ## describe_health_service_status_for_organization
    describe_health_service_status_for_org()

    ## describe_events_for_organization(**kwargs)
    describe_events_for_org()

    ## describe_affected_accounts
    describe_affected_accounts()

    ## transfer dict data to list
    dict_to_list()
    
    ## save event data to csv file
    write_to_csv()

    ## upload the csv file to S3 bucket
    upload_to_s3(file_name = csvFileName, bucket = bucketName, key = csvFileName)

    ## create manifest file, and save it to S3 bucket
    create_manifest()
    upload_to_s3(file_name = "manifests3.json", bucket = bucketName, key = "manifests3.json")

