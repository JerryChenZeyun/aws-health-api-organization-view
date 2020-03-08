# Building Organization Service Health Check Solution with Cloud9 and QuickSight
This lab is intended to showcase the Health API Organization View feature. Organization View is intended to aggregate Personal Health Dashboard/Health events at the PAYER account level within an organization. Thus it requires an Organization hierarchy, including linked accounts. Furthermore, for the data required to be aggregated at the PAYER account level, it needs to be enabled prior to the Personal Health Dashboard notification being created.

<br />
<br />

# Introduction
This lab aims to show users how easy it is to call AWS health API at organization level through Cloud9. The python code initially runs locally in the Cloud9 environment, where we will upload the health status data to S3 bucket, and then visualise the data using QuickSight. Optionally, user can consider to integrate email SNS to get notification upon the conditions setup by the operation team.

![Image of Yaktocat](https://github.com/JerryChenZeyun/aws-health-api-organization-view/blob/master/media/Screen%20Shot%202020-02-23%20at%209.02.34%20pm.png)


# Setup
1. Goto to AWS Console, select Cloud9 service (In N.Virginia Region -- "us-east-1"). Or simply click the following link:
https://console.aws.amazon.com/cloud9/home?region=us-east-1

2. Create a new Cloud9 environment by Clicking the "Create Environment" button
![Image of Yaktocat](https://github.com/JerryChenZeyun/aws-health-api-organization-view/blob/master/media/Screen%20Shot%202020-02-23%20at%209.30.48%20pm.png)

3. Give a name to the new environment. In this demo, we can name it as "demo-env". Then click "Next step".
![Image of Yaktocat](https://github.com/JerryChenZeyun/aws-health-api-organization-view/blob/master/media/Screen%20Shot%202020-02-23%20at%209.32.55%20pm.png)

4. Accept other default settings, click "Next step"
![Image of Yaktocat](https://github.com/JerryChenZeyun/aws-health-api-organization-view/blob/master/media/Screen%20Shot%202020-02-23%20at%209.34.54%20pm.png)

5. In the "Review" page, review the environment configurations, and click "Create environment" to kickoff the creation process. It would take around 1 to 2 mins for the Cloud9 environment to be provisioned.
![Image of Yaktocat](https://github.com/JerryChenZeyun/aws-health-api-organization-view/blob/master/media/Screen%20Shot%202020-03-06%20at%204.02.42%20pm.png)

6. Once the Cloud9 environment has been provisioned, use the following command to update the boto3 library -- as the current default library version (1.10.41) doesn't support the latest AWS health API for Organization.

    ec2-user:~/environment $ `python -m pip install boto3 -t ./`

7. As we need to use python pandas module to translate the json data into csv file, please use the following command to install pandas module

    ec2-user:~/environment $ `python -m pip install pandas --user`
    
8. Now the environment has almost ready. So please use the following command to download the project to Cloud9, and copy the "health_org_demo.py" date to the environment folder.

    ec2-user:~/environment $ `git clone https://github.com/JerryChenZeyun/aws-health-api-organization-view.git`
    
    ec2-user:~/environment $ `cp /home/ec2-user/environment/aws-health-api-organization-view/health_org_demo.py /home/ec2-user/environment/health_org_demo.py`
    
9. Create the S3 bucket to host the event data fed back from the organization health api call. Lab user can go to S3 console (`https://s3.console.aws.amazon.com/s3/home?region=us-east-1`) to create a new bucket. Simply give the new bucket a name,  then accept all the default setting and keep on clicking "Next", and finally click "Create Bucket" to finalise S3 bucket creation. You may jot down the name which is needed in next step.

    For those user need more guidance on creating the new bucket, you may refer to the [Create new S3 bucket](#create-new-s3-bucket) in appendix section.

10. Use the Cloud9 editor environment to change the following parameter value based on your Lab environment info:

    1) accountId - change it to your 12 digit account id number. You can find your AWS account id via this link:
    https://console.aws.amazon.com/billing/home?#/account
    
    2) bucketName - change it to your bucket name, which is used to host the data fetched by the health api. You can find your buckets via this link:
    https://s3.console.aws.amazon.com/s3/home

    Once the above 2 parameters have been updated, you can simply save the python file. 
    ("Command" + "S" for MAC, or "Control" + "S" for Windows)

![Image of Yaktocat](https://github.com/JerryChenZeyun/aws-health-api-organization-view/blob/master/media/Screen%20Shot%202020-02-27%20at%208.24.34%20pm.png)


   For those who interested in digging out the api call functions, you may take a quick look at the python code.    



11. Execute the python script -- Use the following command in Cloud9 to proceed:

    ec2-user:~/environment $ `python health_org_demo.py`


   Once the code has been executed successfully, You can see the output from Cloud9, showing the health status info summary, and detail health info in json format. 
   
![Image of Yaktocat](https://github.com/JerryChenZeyun/aws-health-api-organization-view/blob/master/media/Screen%20Shot%202020-02-27%20at%208.35.19%20pm.png)

12. Analyze the health event data printed at the Cloud9 terminal. In the Cloud9 terminal, we will find the json format data retrieved from health api call at organization level. 


# Visualize the health event csv data through QuickSight

After the python script has been executed, the health status data would be stored in S3 bucket as csv file. We can utilise various tooling to visualise the dataset. In this Lab, we are going to use QuickSight.

1. Go to the following QuickSight link to generate the view of the dataset
https://us-east-1.quicksight.aws.amazon.com/sn/start

2. Choose "New analysis" at the top left corner of the QuickSight page

![Image of Yaktocat](https://github.com/JerryChenZeyun/aws-health-api-organization-view/blob/master/media/Screen%20Shot%202020-02-27%20at%209.46.46%20pm.png)

3. Choose "New data set" at the top left corner of the page

![Image of Yaktocat](https://github.com/JerryChenZeyun/aws-health-api-organization-view/blob/master/media/Screen%20Shot%202020-02-27%20at%209.52.27%20pm.png)

4. Select S3, then fill in Data source name (e.g. event_data_file), use the following link to specify the manifest file:
https://my-test-bucket-20191011.s3-ap-southeast-2.amazonaws.com/manifest.json

   Then hit "Connect", and then click "Visualize" to proceed. 

![Image of Yaktocat](https://github.com/JerryChenZeyun/aws-health-api-organization-view/blob/master/media/Screen%20Shot%202020-02-27%20at%209.58.07%20pm.png)

5. Experience the dataset visualization -- at this step, user can simply select or drag/drop via QuickSight GUI to visualize the dataset based on specific need. the screenshots show visualize the whole dataset, and only the "region" data for the health events within the organization.

![Image of Yaktocat](https://github.com/JerryChenZeyun/aws-health-api-organization-view/blob/master/media/Screen%20Shot%202020-02-27%20at%2010.04.33%20pm.png)

![Image of Yaktocat](https://github.com/JerryChenZeyun/aws-health-api-organization-view/blob/master/media/Screen%20Shot%202020-02-27%20at%2010.04.52%20pm.png)


# Clean Up Step

Goto to Cloud9 dashboard in AWS Console via the following link. Select your IDE environment and select "Delete".

'https://console.aws.amazon.com/cloud9/home?region=us-east-1'

<br />
<br />




# Appendix

# Create new S3 bucket

This section give you more detailed guidance on how to create the S3 bucket to host data fed back from Organization Health API Call. Please follow these steps to complete the bucket creation:

1. Go to the following link to access AWS S3 service, then click "Create bucket".
    `https://s3.console.aws.amazon.com/s3/home?region=us-east-1`
    
![Image of Yaktocat](https://github.com/JerryChenZeyun/aws-health-api-organization-view/blob/master/media/Screen%20Shot%202020-03-08%20at%209.02.24%20pm.png)


# Setting up QuickSight 

For those AWS accounts that use QuickSight for the first time, users need to explicitely sign up for QuickSight. Please follow the following steps:

1. Go to follow link to access AWS QuickSight service, then click "Sign up for QuickSight".

   `https://us-east-1.quicksight.aws.amazon.com/sn/start`

![Image of Yaktocat](https://github.com/JerryChenZeyun/aws-health-api-organization-view/blob/master/media/Screen%20Shot%202020-03-08%20at%204.48.39%20pm.png)

2. In the QuickSight account selection page, please select "Standard" edition for this lab as shown below. Then click "Continue" at the bottom right corner.

![Image of Yaktocat](https://github.com/JerryChenZeyun/aws-health-api-organization-view/blob/master/media/Screen%20Shot%202020-03-08%20at%204.56.48%20pm.png)

