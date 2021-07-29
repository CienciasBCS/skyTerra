import json
import string
import random

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


def upload_file_to_s3(file, file_key):
    s3 = boto3.client('s3')
    try:
        s3.upload_fileobj(
                file,
                current_app.config['BUCKET'],
                file_key,
            )
    except Exception as e:
        print("Something Happened: ", e)
        return e
    return False


def get_random_code(size=6, chars=string.ascii_uppercase + string.digits):

    return ''.join(random.choice(chars) for _ in range(size))