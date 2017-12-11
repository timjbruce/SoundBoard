
import json
import urllib.parse
import boto3
import uuid

#setup this function to run anytime a new file is placed in the s3 bucket that is created
#via sbSetup.py

print('Loading function')

s3 = boto3.client('s3')
dynamo = boto3.resource('dynamodb')

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    print(bucket)
    print(key)
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        print("CONTENT TYPE: " + response['ContentType'])
        #skip directories
        if(response['ContentType']=='application/x-directory'):
            return(response['ContentType'])
        i = key.find('/')
        # store to Dynamo
        table = dynamo.Table("soundboard")
        s = str(uuid.uuid4())
        table.put_item(Item={ "uuid": s, "filename":key, "show":"unknown", } )
        if(i>-1):
            #store show record, too
            show_name=key[0:i]
            table.put_item(Item={ "uuid": s, "filename":key, "show":show_name, } )
        return response['ContentType']
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
