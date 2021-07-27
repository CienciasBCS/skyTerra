import json

from flask import current_app
from sqlalchemy import create_engine
import boto3

def get_json_s3(bucket, full_key):
    s3 = boto3.resource('s3')

    content_object = s3.Object(bucket, full_key)
    file_content = content_object.get()['Body'].read().decode('latin1')
    js = json.loads(file_content)
    return js

def get_conn_sb_tar():
    engine = create_engine(current_app.config['DB_SB_URI'])
    conn = engine.connect()
    
    return conn


def upload_file_to_s3(file, bucket_name, file_key):
    s3 = boto3.client('s3')
    try:
        s3.upload_fileobj(
                file,
                bucket_name,
                file_key,
            )
    except Exception as e:
        # This is a catch all exception, edit this part to fit your needs.
        print("Something Happened: ", e)
        return e
    return False