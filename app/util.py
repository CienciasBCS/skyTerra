import json
import boto3

def get_json_s3(bucket, full_key):
    s3 = boto3.resource('s3')

    content_object = s3.Object(bucket, full_key)
    file_content = content_object.get()['Body'].read().decode('latin1')
    js = json.loads(file_content)
    return js