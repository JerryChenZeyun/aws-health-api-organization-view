# Building Organization Service Health Check Solution with Cloud9 and QuickSight
Showcase retrieving service health status via Cloud9 by calling health api at organization level, and visualise the health status data through QuickSight.

# Introduction
This lab aims to show users how easy it is to call AWS health API at organization level through Cloud9. The python code initially runs locally in the Cloud9 environment, where we will upload the health status data to S3 bucket, and then visualise the data using QuickSight. Optionally, user can consider to integrate email SNS to get notification upon the conditions setup by the operation team.

![Image of Yaktocat](https://github.com/JerryChenZeyun/aws-health-api-organization-view/blob/master/Screen%20Shot%202020-02-23%20at%209.02.34%20pm.png)

# Setup
1. Goto to AWS Console, select Cloud9 service (In N.Virginia Region -- "us-east-1"). Or simply click the following link:
https://console.aws.amazon.com/cloud9/home?region=us-east-1

2. Create a new Cloud9 environment by Clicking the "Create Environment" button

3. Give a name to the new environment. In this demo, we can name it as "demo-env". 

4. Accept other default settings ()



