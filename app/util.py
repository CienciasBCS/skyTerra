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