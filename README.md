# Building Organization Service Health Check Solution with Cloud9 and QuickSight
Showcase retrieving service health status via Cloud9 by calling health api at organization level, and visualise the health status data through QuickSight.


# Introduction
This lab aims to show users how easy it is to call AWS health API at organization level through Cloud9. The python code initially runs locally in the Cloud9 environment, where we will upload the health status data to S3 bucket, and then visualise the data using QuickSight. Optionally, user can consider to integrate email SNS to get notification upon the conditions setup by the operation team.

![Image of Yaktocat](https://github.com/JerryChenZeyun/aws-health-api-organization-view/blob/master/Screen%20Shot%202020-02-23%20at%209.02.34%20pm.png)


# Setup
1. Goto to AWS Console, select Cloud9 service (In N.Virginia Region -- "us-east-1"). Or simply click the following link:
https://console.aws.amazon.com/cloud9/home?region=us-east-1

2. Create a new Cloud9 environment by Clicking the "Create Environment" button
![Image of Yaktocat](https://github.com/JerryChenZeyun/aws-health-api-organization-view/blob/master/Screen%20Shot%202020-02-23%20at%209.30.48%20pm.png)

3. Give a name to the new environment. In this demo, we can name it as "demo-env". 
![Image of Yaktocat](https://github.com/JerryChenZeyun/aws-health-api-organization-view/blob/master/Screen%20Shot%202020-02-23%20at%209.32.55%20pm.png)

4. Accept other default settings, click "Next step", and then finalise the creation by clicking "Create environment".
![Image of Yaktocat](https://github.com/JerryChenZeyun/aws-health-api-organization-view/blob/master/Screen%20Shot%202020-02-23%20at%209.34.54%20pm.png)

5. Once the Cloud9 environment has been provisioned, use the following command to update the boto3 library -- as the current default library version (1.10.41) doesn't support the latest AWS health API for Organization.

    ec2-user:~/environment $ `python -m pip install boto3 -t ./`

6. As we need to use python pandas module to translate the json data into csv file, please use the following command to install pandas module

    ec2-user:~/environment $ `python -m pip install pandas --user`
    
7. Now the environment has almost ready. So please use the following command to download the project to Cloud9, and copy the "health_org_demo.py" date to the environment folder.

    ec2-user:~/environment $ `git clone https://github.com/JerryChenZeyun/aws-health-api-organization-view.git`
    
    ec2-user:~/environment $ `cp /home/ec2-user/environment/aws-health-api-organization-view/health_org_demo.py /home/ec2-user/environment/health_org_demo.py`

8. Use the Cloud9 editor environment to change the following parameter value based on your Lab environment info:

    1) accountId - change it to your 12 digit account id number. You can find your AWS account id via this link:
    https://console.aws.amazon.com/billing/home?#/account
    
    2) bucketName - change it to your bucket name, which is used to host the data fetched by the health api. You can find your buckets via this link:
    https://s3.console.aws.amazon.com/s3/home

    Once the above 2 parameters have been updated, you can simply save the python file. 
    ("Command" + "S" for MAC, or "Control" + "S" for Windows)

![Image of Yaktocat](https://github.com/JerryChenZeyun/aws-health-api-organization-view/blob/master/Screen%20Shot%202020-02-27%20at%208.24.34%20pm.png)


   For those who interested in digging out the api call functions, you may take a quick look at the python code.    



9. Execute the python script -- Use the following command in Cloud9 to proceed:

    ec2-user:~/environment $ `python health_org_demo.py`


   Once the code has been executed successfully, You can see the output from Cloud9, showing the health status info summary, and detail health info in json format. 
   
![Image of Yaktocat](https://github.com/JerryChenZeyun/aws-health-api-organization-view/blob/master/Screen%20Shot%202020-02-27%20at%208.35.19%20pm.png)

10. Analyze the health event data printed at the Cloud9 terminal. In the Cloud9 terminal, we will find the json format data retrieved from health api call at organization level. 


# Visualize the health event csv data through QuickSight

After the python script has been executed, the health status data would be stored in S3 bucket as csv file. We can utilise various tooling to visualise the dataset. In this Lab, we are going to use QuickSight.

1. Go to the following QuickSight link to generate the view of the dataset
https://us-east-1.quicksight.aws.amazon.com/sn/start

2. Choose "New analysis" at the top left corner of the QuickSight page

![Image of Yaktocat](https://github.com/JerryChenZeyun/aws-health-api-organization-view/blob/master/Screen%20Shot%202020-02-27%20at%209.46.46%20pm.png)

3. Choose "New data set" at the top left corner of the page

![Image of Yaktocat](https://github.com/JerryChenZeyun/aws-health-api-organization-view/blob/master/Screen%20Shot%202020-02-27%20at%209.52.27%20pm.png)



