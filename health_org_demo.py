####################################################################################################################################################################################
# Script Function: Demonstrate AWS Health API for Organization View
# Author: JC
# Time: 2020.11.03
# Version: 1.2
# Execution requirements: 
#   Update the "bucketName" value following the instruction from Step 10 in  https://github.com/JerryChenZeyun/aws-health-api-organization-view/blob/master/README.md#setup
####################################################################################################################################################################################

import logging
import datetime
import boto3
import json
from botocore.exceptions import ClientError
import os
import pandas as pd

####################################################################################################################################################################################
bucketName = 'YOUR-S3-BUCKET-NAME-HERE'
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
impactedAccount_List = []
eventDescription_List = []
impactedEntity_List = []

# time encoder class
class DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super(DatetimeEncoder, obj).default(obj)
        except TypeError:
            return str(obj)

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
        print("s3 upload success -- uploaded " + file_name + " to the bucket: " + bucket)
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
            'statusCode': statusCode_list,
            'impactedAccount': impactedAccount_List,
            'impactedEntity': impactedEntity_List,
            'eventDescription': eventDescription_List
        }
    )
    event_data_file = open(csvFileName, "w")
    event_data_file.write(whole_table.to_csv(index=False))
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
    event_paginator = client.get_paginator('describe_events_for_organization')
    event_page_iterator = event_paginator.paginate()
    
    for event_page in event_page_iterator:
        json_event = json.dumps(event_page, cls=DatetimeEncoder)
        parsed_event = json.loads(json_event)
        
        events = parsed_event.get("events")
        
        for event in events:
            arn_list.append(event.get("arn"))
            service_list.append(event.get("service"))
            eventTypeCode_list.append(event.get("eventTypeCode"))
            eventTypeCategory_list.append(event.get("eventTypeCategory"))
            region_list.append(event.get("region"))
            startTime_list.append(event.get("startTime"))
            lastUpdatedTime_list.append(event.get("lastUpdatedTime"))
            statusCode_list.append(event.get("statusCode"))
            if (event.get("statusCode") == "open"):
                endTime_list.append("NULL")
            elif (event.get("statusCode") == "closed"):
                endTime_list.append(event.get("endTime"))

            response = client.describe_event_details(eventArns = [event.get("arn")], locale = "en")
            json_response = json.dumps(response, cls=DatetimeEncoder)
            parsed_response = json.loads (json_response)
            eventDescription_List.append(parsed_response["successfulSet"][0]["eventDescription"]["latestDescription"])

    print("\n#########################################################################\n")
    print("describe_events_for_organization response - Total events:", len(arn_list))
    print("\n")
    print("These events are related to the following services:\n", service_list)
    print("\n#########################################################################\n")
    return(True)

## describe_affected_accounts
def describe_affected_accounts(event_arn):
    affectedAccounts = []
    client = boto3.client('health')
    event_accounts_paginator = client.get_paginator('describe_affected_accounts_for_organization')
    
    event_accounts_page_iterator = event_accounts_paginator.paginate(eventArn=event_arn)
        
    for event_accounts_page in event_accounts_page_iterator:
        json_event_accounts = json.dumps(event_accounts_page, cls=DatetimeEncoder)
        parsed_event_accounts = json.loads (json_event_accounts)
            
        if((parsed_event_accounts['affectedAccounts']) == "[]"):
            affectedAccounts = affectedAccounts +"[]"
        else:
            affectedAccounts = affectedAccounts + (parsed_event_accounts['affectedAccounts'])
        print("For service event arn: {}".format(arn))
        print("Affected accounts are: {}".format(affectedAccounts))
    
    return(affectedAccounts)

## Retrieve account id automatically
def get_account_id():
    return(boto3.client('sts').get_caller_identity().get('Account'))

## describe_affected_entities_for_organization(**kwargs)
def describe_affected_entities(event_arn):
    affectedEntities = []
    affectedEntities_sub_list = []
    client = boto3.client('health')
    affected_accounts = describe_affected_accounts(event_arn)
    
    for affected_account in affected_accounts:
        affected_account = ''.join(str(e) for e in affected_account)
        
        #If there's no affected account for this event, the 'affected account' will be filled by '[]'
        if(not affected_account):
            affected_account = '[]'
        
        print("affected_account: ", affected_account)
        print("affected account type:", type(affected_account))
        
        event_entities_paginator = client.get_paginator('describe_affected_entities_for_organization')
        event_entities_page_iterator = event_entities_paginator.paginate(
        organizationEntityFilters=[
            {    
                'awsAccountId': affected_account,
                'eventArn': event_arn
            }
            ]
        )
        
        affectedEntities_sub_list = []
        
        for event_entities_page in event_entities_page_iterator:
            json_event_entities = json.dumps(event_entities_page, cls=DatetimeEncoder)
            parsed_event_entities = json.loads (json_event_entities)
            print("for event {} and affected account {}: ".format(event_arn, affected_account))
            print("event entities list are: {} \n".format(parsed_event_entities))
                
            for entity in parsed_event_entities['entities']:
                
                if((entity['entityValue']) != "[]"):
                    affectedEntities_sub_list.append(entity['entityValue'])
            
            print("\n#########################################################################\n")
            print("affected entities list are:", affectedEntities_sub_list)
            print("\n#########################################################################\n")
                
        if(len(affectedEntities_sub_list) == 0):
            affectedEntities = affectedEntities + "[]"
        else:
            affectedEntities = affectedEntities + affectedEntities_sub_list
    return(affectedEntities)


# Main part of Script
# -------------------
if __name__ == "__main__":  

    ## Enable the health service in organization level
    enable_health_org()

    ## describe_health_service_status_for_organization
    describe_health_service_status_for_org()

    ## describe_events_for_organization(**kwargs)
    describe_events_for_org()

    ## describe_affected_accounts & describe_affected_entities
    for arn in arn_list:
        eventAffectedAccounts = describe_affected_accounts(arn)
        print ("eventAffectedAccounts:",eventAffectedAccounts)
        impactedAccount_List.append(eventAffectedAccounts)
        
        eventAffectedEntities = describe_affected_entities(arn)
        print ("eventAffectedEntities:",eventAffectedEntities)
        impactedEntity_List.append(eventAffectedEntities)
    
    print("complete impacted account list:", impactedAccount_List)    
    print("complete impacted entity list:", impactedEntity_List)
    
    ## save event data to csv file
    write_to_csv()

    ## upload the csv file to S3 bucket
    upload_to_s3(file_name=csvFileName, bucket=bucketName, key=csvFileName)

    ## create manifest file, and save it to S3 bucket
    create_manifest()
    upload_to_s3(file_name="manifests3.json", bucket=bucketName, key="manifests3.json")

