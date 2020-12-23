####################################################################################################################################################################################
# Script Function: Demonstrate AWS Health API for Organization View
# Author: JC
# Time: 2020.12.24
# Version: 1.4
# Execution requirements: 
#   Update the "bucketName" value following the instruction from Step 10 in  https://github.com/JerryChenZeyun/aws-health-api-organization-view/blob/master/README.md#setup
####################################################################################################################################################################################
import json
import logging
from datetime import datetime
from dateutil import parser
import boto3
import json
import csv
from itertools import zip_longest
from botocore.exceptions import ClientError
import os
import urllib.request
import fileinput
from time import sleep

####################################################################################################################################################################################
bucketName = os.environ.get('s3_bucket_name')
####################################################################################################################################################################################

csvFileName = 'event_data_file.csv'
manifest_url = 'https://raw.githubusercontent.com/JerryChenZeyun/aws-health-api-organization-view/master/manifest.json'

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

def enable_health_org():
    client = boto3.client('health', 'us-east-1')
    try:
        response = client.enable_health_service_access_for_organization()
        print("enable health api at organization level success")
    except ClientError as e:
        logging.error(e)
        print("enable health api at organization level error occurs:", e)
    print(response)
    print("\n#########################################################################\n")
    print("Health Service has been enabled at AWS Organization Level -- Done!")
    print("\n#########################################################################\n")

# time encoder class
class DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super(DatetimeEncoder, obj).default(obj)
        except TypeError:
            return str(obj)

## Check if the health data has been stored in the S3 bucket. So lambda will know if it needs to pull the whole set of health data
def get_s3_file_status():
    s3 = boto3.resource('s3')
    try:
        s3.Object(bucketName, csvFileName).load()
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            # The object does not exist.
            print ("data file doesn't exist.")
            return (False)   
    print ("data file does exist.")
    return (True)

# Combine the latest health data with historical data
def data_merge(file1, file2, combined_file):
    lambda_file1 = '/tmp/' + file1
    lambda_file2 = '/tmp/' + file2
    s3 = boto3.client("s3")
    s3.download_file(bucketName, file1, lambda_file1)
    s3.download_file(bucketName, file2, lambda_file2)
    reader1 = csv.reader(open(lambda_file1))
    reader2 = csv.reader(open(lambda_file2))
    file_name = "/tmp/" + combined_file
    f = open(file_name, "w")
    writer = csv.writer(f)

    for row in reader1:
        writer.writerow(row)
    for row in reader2:
        writer.writerow(row)
    f.close()

    tempfile = "/tmp/tmp_" + combined_file
    inFile = open(file_name,'r')
    outFile = open(tempfile,'w')
    listLines = []

    for line in inFile:
        if line in listLines:
            continue
        else:
            outFile.write(line)
            listLines.append(line)
    outFile.close()
    inFile.close()

## Upload the organization events json message to S3 file
def upload_to_s3(file_name, bucket, key):
    """Upload a file to an S3 bucket
    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """    
    lambdaFileName = '/tmp/' + file_name
    s3 = boto3.resource('s3')
    try:
        s3.meta.client.upload_file(lambdaFileName, bucket, key)
        print("s3 upload success -- uploaded " + key + " to the bucket: " + bucket)
    except ClientError as e:
        logging.error(e)
        return False
        print("s3 upload error occurs", e)
    return True

# Store event data info into csv file
def write_to_csv(file_name):
    whole_table = [arn_list, service_list, eventTypeCode_list, eventTypeCategory_list, region_list, startTime_list, 
    endTime_list, lastUpdatedTime_list, statusCode_list, impactedAccount_List, impactedEntity_List, eventDescription_List]
    export_data = zip_longest(*whole_table, fillvalue = '')
    
    lambdaFileName = '/tmp/' + file_name
    with open(lambdaFileName, 'w', encoding="utf-8", newline='') as myfile:
        wr = csv.writer(myfile)
        wr.writerow(("arn", "service", "eventTypeCode", "eventTypeCategory", "region", "startTime", "endTime", "lastUpdatedTime", 
        "statusCode", "impactedAccount", "impactedEntity", "eventDescription"))
        wr.writerows(export_data)
    myfile.close()
    
    print("\n#########################################################################\n")
    print("Event data saved to CSV file.")
    print("\n#########################################################################\n")

## Create the Manifest file, and save it to the user specified S3 bucket
def create_manifest():
    """Create a Manifest file to an user specified S3 bucket
    This is required when user need to visualise the event data hosted in S3 bucket via QuickSight
    """
    # download the manifest file template
    urllib.request.urlretrieve(manifest_url, '/tmp/manifest.json')
    
    file_path_ori = "/tmp" + "/manifest.json"
    file_path_new = "/tmp" + "/manifests3.json"

    with open(file_path_ori, "rt") as fin:
        with open(file_path_new, "wt") as fout:
            for line in fin:
                fout.write(line.replace('bucket-name', bucketName))

## describe_health_service_status_for_organization
def describe_health_service_status_for_org():
    client = boto3.client('health', 'us-east-1')
    response = client.describe_health_service_status_for_organization()
    print(response)
    print("\n#########################################################################\n")

## describe_events_for_organization(**kwargs)
def describe_events_for_org(start_time):
    client = boto3.client('health', 'us-east-1')
    event_paginator = client.get_paginator('describe_events_for_organization')
    event_page_iterator = event_paginator.paginate(
        filter={
            'lastUpdatedTime':{
                'from': start_time
            }
        }
    )
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
            else:
                endTime_list.append("NULL")

            response = client.describe_event_details(eventArns = [event.get("arn")], locale = "en")
            json_response = json.dumps(response, cls=DatetimeEncoder)
            parsed_response = json.loads (json_response)
            eventDescription_List.append(parsed_response["successfulSet"][0]["eventDescription"]["latestDescription"])

    print("\n#########################################################################\n")
    print("describe_events_for_organization response - Total events:{}".format(len(arn_list)))
    print("These events are related to the following services:\n", service_list)
    print("\n#########################################################################\n")
    return(True)

## read the latest event time
def check_latest_event():
    last_update_time = []
    lambdaFileName = '/tmp/' + csvFileName
    s3 = boto3.resource('s3')
    obj = s3.Object(bucketName, csvFileName)
    s3.Bucket(bucketName).download_file(csvFileName, lambdaFileName)
    
    with open(lambdaFileName, 'r') as file:
        reader = csv.reader(file)
        row1 = next(reader)
        column = 0

        for item in row1:
            if (item == 'lastUpdatedTime'):
                break
            else:
                column += 1
        
        for row in reader:
            if (row[column] != "lastUpdatedTime"):
                #date_time_obj = datetime.datetime.strptime(row[column], '%y-%m-%d %H:%M:%S.%f%z')
                strUpdate = parser.parse(row[column])
                last_update_time.append(strUpdate)
        
    return(max(last_update_time))

## describe_affected_accounts
def describe_affected_accounts(event_arn):
    affectedAccounts = []
    client = boto3.client('health', 'us-east-1')
    event_accounts_paginator = client.get_paginator('describe_affected_accounts_for_organization')
    
    event_accounts_page_iterator = event_accounts_paginator.paginate(eventArn=event_arn)
        
    for event_accounts_page in event_accounts_page_iterator:
        json_event_accounts = json.dumps(event_accounts_page, cls=DatetimeEncoder)
        parsed_event_accounts = json.loads (json_event_accounts)
            
        if((parsed_event_accounts['affectedAccounts']) == "[]"):
            affectedAccounts = affectedAccounts +"[]"
        else:
            affectedAccounts = affectedAccounts + (parsed_event_accounts['affectedAccounts'])
        print("For service event arn: {}".format(event_arn))
        print("Affected accounts are: {}".format(affectedAccounts))
    
    return(affectedAccounts)

## Retrieve account id automatically
def get_account_id():
    return(boto3.client('sts').get_caller_identity().get('Account'))

## describe_affected_entities_for_organization(**kwargs)
def describe_affected_entities(event_arn):
    affectedEntities = []
    affectedEntities_sub_list = []
    client = boto3.client('health', 'us-east-1')
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

def lambda_handler(event, context):
    # TODO implement
    arn_list.clear()
    service_list.clear()
    eventTypeCode_list.clear()
    eventTypeCategory_list.clear()
    region_list.clear()
    startTime_list.clear()
    endTime_list.clear()
    lastUpdatedTime_list.clear()
    statusCode_list.clear()
    impactedAccount_List.clear()
    eventDescription_List.clear()
    impactedEntity_List.clear()
    
    print("boto3 version is ---", boto3.__version__)

    # If the data file not exist, then lambda pull out the whole health dataset. Otherwise, Lambda just pull the delta dataset.
    if (not (get_s3_file_status())):
        # Enable the health service in organization level
        enable_health_org()
        ## describe_health_service_status_for_organization
        describe_health_service_status_for_org()
        ## describe_events_for_organization(**kwargs)
        describe_events_for_org(datetime(2015,1,1))
        ## describe_affected_accounts & describe_affected_entities
        for arn in arn_list:
            eventAffectedAccounts = describe_affected_accounts(arn)
            sleep(1)
            print ("eventAffectedAccounts:",eventAffectedAccounts)
            impactedAccount_List.append(eventAffectedAccounts)
            sleep(1)            
            eventAffectedEntities = describe_affected_entities(arn)
            print ("eventAffectedEntities:",eventAffectedEntities)
            impactedEntity_List.append(eventAffectedEntities)
        
        print("complete impacted account list:", impactedAccount_List)    
        print("complete impacted entity list:", impactedEntity_List)
        
        ## create manifest file, and save it to S3 bucket
        create_manifest()
        upload_to_s3(file_name="manifests3.json", bucket=bucketName, key="manifests3.json")
        
        ## save event data to csv file
        write_to_csv(csvFileName)

        ## upload the csv file to S3 bucket
        upload_to_s3(file_name=csvFileName, bucket=bucketName, key=csvFileName)
    
    else:
        latest_time = check_latest_event()
        print("latest_time is: ", latest_time )
        ## describe_events_for_organization(**kwargs)
        describe_events_for_org(latest_time)

        ## Check if there's updated event data
        if (len(arn_list) >= 1): 
            ## describe_affected_accounts & describe_affected_entities
            for arn in arn_list:
                eventAffectedAccounts = describe_affected_accounts(arn)
                print ("eventAffectedAccounts:",eventAffectedAccounts)
                impactedAccount_List.append(eventAffectedAccounts)
                sleep(1)
                
                eventAffectedEntities = describe_affected_entities(arn)
                print ("eventAffectedEntities:",eventAffectedEntities)
                impactedEntity_List.append(eventAffectedEntities)
                sleep(1)
            
            print("complete impacted account list:", impactedAccount_List)    
            print("complete impacted entity list:", impactedEntity_List)

            ## save event data to csv file
            new_file = 'event_data_file_recent.csv'
            write_to_csv(new_file)

            ## upload the csv file to S3 bucket
            upload_to_s3(file_name=new_file, bucket=bucketName, key=new_file)

            ## merge the latest data with historical data into csvFileName
            data_merge(new_file, csvFileName, 'combined_new_file.csv')

            ## upload the csv file to S3 bucket
            upload_to_s3(file_name='tmp_combined_new_file.csv', bucket=bucketName, key=csvFileName)

    return {
        'statusCode': 200,
        'body': json.dumps('AWS Service Health Data has been polled and uploaded to the specified S3 bucket!')
    }
