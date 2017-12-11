import boto3

#create s3 bucket with public website hosting for Alexa


#create the dynamo table
import sys
import boto3
from os import walk
import datetime
import time
from datetime import timedelta

def checkResponse(response):
    if response['ResponseMetadata']['HTTPStatusCode']==200:
        return True
    else:
        return False

def createDatabase(dynClient, uritablename):
    response = dynClient.create_table(
        AttributeDefinitions=[
            {
                'AttributeName':'show',
                'AttributeType':"S"
            },
            {
                'AttributeName':'uuid',
                'AttributeType':"S"
            }
        ],
        TableName=uritablename,
        KeySchema=[
            {
                'AttributeName': 'show',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'uuid',
                'KeyType': 'RANGE'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
        )

    if (checkResponse(response)):
        print ('Table {0} created'.format(uritablename))
    else:
        print ('Could not create table {0}.\n{1]}'.format(uritablename, respsonse))

def createBucket(s3client, bucketname, websitehosting):

    #create the bucket
    #print ('creating bucket '+ bucketname)
    response = s3client.create_bucket(Bucket=bucketname)
    if (checkResponse(response)):
        print ('Bucket {0} created'.format(bucketname))
    else:
        print ('Could not create bucket {0}\n{1}'.format(bucketname, response))
        return

    #add default encryption
    response = s3client.put_bucket_encryption(
        Bucket=bucketname,
        ServerSideEncryptionConfiguration={
            'Rules': [
                {
                    'ApplyServerSideEncryptionByDefault': {
                        'SSEAlgorithm': 'AES256'
                    }
                }
            ]
        }
    )
    #print ("Encryption ")
    if (checkResponse(response)):
        print ('Encrytpion added to Bucket {0}'.format(bucketname))
    else:
        print ('Could not add encryption to bucket {0}\n{1}'.format(bucketname, response))
        return


    #turn on web hosting
    if(websitehosting):
        response = s3client.put_bucket_website(
            Bucket=bucketname,
            WebsiteConfiguration={
                'ErrorDocument': {
                    'Key': 'error.html'
                },
                'IndexDocument': {
                    'Suffix': 'index.html'
                },
            }
        )
        #print ("Hosting")
        if (checkResponse(response)):
            print ('Webhosting added to Bucket {0}'.format(bucketname))
        else:
            print ('Could not add Webhosting to bucket {0}.\n{1}'.format(bucketname, response))
            return

def main(args):

    #this script relies on the aws cli being installed and configured with user
    #credentials prior to being run
    #it uses [default] to set user and region - please use appropriately

    #check for parameters
    if len(args)==2:
    #we have the right number, store it off
        webbucket = args[1]
    else:
        print( 'correct usage is python {0} <webbucket> '.format(args[0]) )
        sys.exit()

    #variables for the names of objects to be created
    #tablename is the only one to match the lambda@edge call
    tablename = 'soundboard'

    #create the necessary clients
    s3client = boto3.client('s3')
    dynclient = boto3.client('dynamodb')

    #create the buckets first - these are dependencies for CF distro and
    #since they are in the public namespace, we want to make sure these are held for
    #the deployment
    createBucket(s3client, webbucket, True)

    print("Buckets are done")

    #setup the table and add records
    createDatabase(dynclient, tablename)

main(sys.argv)
