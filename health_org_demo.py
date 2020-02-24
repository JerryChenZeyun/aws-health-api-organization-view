##########################################################################################
# Script Function: Demonstrate AWS Health API for Organization View
# Author: JC
# Time: 2020.02.23
# Version: 1.0
##########################################################################################

import boto3
import logging
from botocore.exceptions import ClientError
import json
import datetime
import pandas as pd

accountId = '910003606845'
bucketName = 'my-test-bucket-20191011'
csvFileName = 'event_data_file_' + str(datetime.datetime.now())

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
def dict_to_list(event_data):
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

## Wraping up the dict info into json message 
def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

## Send the json message to user email via SNS
def send_email_notification(sent_msg):
    sns_client = boto3.client('sns')
    #json_info = json.dumps(response_org_event, default = myconverter)
    json_info = json.dumps(sent_msg, default = myconverter)
    response = sns_client.publish(
        TopicArn = 'arn:aws:sns:us-east-1:910003606845:test-topic-health',
        Message = json_info,
        Subject = 'API Test',
    )
    #print (response )
    #print(type(json_info))
    #print(json_info)
    print("\n#########################################################################\n")
    print("Notification email sent via SNS.")
    print("\n#########################################################################\n")

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
    



# Main part of Script
# -------------------
if __name__ == "__main__":  


    client = boto3.client('health')

    try:
        response = client.enable_health_service_access_for_organization()
        print("enable health api at organization level success")
    except ClientError as e:
        logging.error(e)
        print("enable health api at organization level error occurs:", e)

    ## Enable the health service in organization level
    
    
    print("\n#########################################################################\n")
    print(response)
    print("\n#########################################################################\n")
    print("Health Service has been enabled at AWS Organization Level -- Done!")
    print("\n#########################################################################\n")

    ## describe_health_service_status_for_organization
    response = client.describe_health_service_status_for_organization()
    print(response)
    print("\n#########################################################################\n")

    ## describe_events_for_organization(**kwargs)
    response_org_event = client.describe_events_for_organization(
        filter={

        }
    )

    print("\n#########################################################################\n")
    print("describe_events_for_organization response is \n")

    print("\n#########################################################################\n")
    print(response_org_event)
    #print(type(response_org_event["events"][0]["arn"]))
    #print(response_org_event["events"][0]["arn"])
    print("\n#########################################################################\n")


    ## describe_affected_accounts_for_organization(**kwargs)
    ## ["events"][1]["arn"] -- This is the EC2 event in Jan

    #ec2_event_arn = "arn:aws:health:ap-southeast-2::event/EC2/AWS_EC2_OPERATIONAL_ISSUE/AWS_EC2_OPERATIONAL_ISSUE_RFMRO_1579740075"
    ec2_event_arn = "arn:aws:health:global::event/CLOUDFRONT/AWS_CLOUDFRONT_OPERATIONAL_ISSUE/AWS_CLOUDFRONT_OPERATIONAL_ISSUE_HQTPY_1580371190"
    ##ec2_event_arn = response["events"][1]["arn"] 
    print(ec2_event_arn)

    response = client.describe_affected_accounts_for_organization(
        eventArn = ec2_event_arn
        #nextToken = 'string',
        #maxResults = 123
        )
    print("\n#########################################################################\n")
    print("Affected accounts for this event are: \n")
    print(response)
    print("\n#########################################################################\n")


    ## describe_events_details_for_organization(**kwargs) 

    response = client.describe_event_details_for_organization(
        organizationEventDetailFilters=[
            {
                'eventArn': ec2_event_arn,
                'awsAccountId': accountId
            },
        ]#,
        #locale='string'
    )

    print("\n#########################################################################\n")
    print("Destribe event details for specific account in organization \n")
    print(response)
    print("\n#########################################################################\n")



    ## describe_affected_entities_for_organization(**kwargs)
    response = client.describe_affected_entities_for_organization(
        organizationEntityFilters=[
            {
                'eventArn': ec2_event_arn,
                'awsAccountId': accountId
            },
        ],
        #locale='string',
        #nextToken='string',
        #maxResults=123
    )

    print("\n#########################################################################\n")
    print("Destribe affected entities for specific account in organization \n")
    print(response)
    print("\n#########################################################################\n")

    ## send notification email via SNS
    send_email_notification(response_org_event)

    ## transfer dict data to list
    dict_to_list(response_org_event)
    
    ## save event data to csv file
    write_to_csv()

    ## upload the csv file to S3 bucket
    upload_to_s3(file_name = csvFileName, bucket = bucketName, key = csvFileName)





