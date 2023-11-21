#! /bin/bash

# This is an example of programmatically launching the llmware AMI from the 'aws' command line
# Details:
#   instance-type: 
#      - t2.2xlarge is the default (non-GPU) instance type
#      - g5.2xlarge or g5.4xlarge are good, cost-effective choices for Nvidia GPU
#   key-name: 
#      - Update the command below to include your key pair name
#   subnet-id:
#      - Update the command below to include the target subnet-id
#   block-device-mappings
#      - The default storage size is 100GB, which is sufficient for modest workloads
#      - If you plan to experiment with many models we recommend increasing that size below
#   tag-specifications:
#      - By default the command below will name the instance "llmware-001". You can change this below

INSTANCE_TYPE=t2.2xlarge
KEY_NAME=YOUR-KEY-NAME
SUBNET_ID=YOUR-SUBNET-ID
STORAGE_SIZE=100
INSTANCE_NAME=llmware-001

aws ec2 run-instances --image-id ami-0eef3676fbf4809e5 \
                      --count 1 \
                      --instance-type $INSTANCE_TYPE \
                      --key-name $KEY_NAME \
                      --subnet-id $SUBNET_ID \
                      --block-device-mappings "DeviceName=/dev/sda1,Ebs={VolumeSize=$STORAGE_SIZE}" \
                      --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]"
                      
