import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = (
        f"mysql://{os.environ['DB_USER_SB']}:{os.environ['DB_PASS_SB']}@{os.environ['DB_HOST_SB']}/{os.environ['DB_NAME']}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DB_SB_URI = f"mysql://{os.environ['DB_USER_SB']}:{os.environ['DB_PASS_SB']}@{os.environ['DB_HOST_SB']}/{os.environ['DB_NAME_SB_TAR']}"

    COGNITO_POOL_ID = os.environ['COGNITO_POOL_ID']
    COGNITO_CLIENT_ID = os.environ['COGNITO_CLIENT_ID']
    COGNITO_CLIENT_SECRET = os.environ['COGNITO_CLIENT_SECRET']
    COGNITO_DOMAIN = os.environ['COGNITO_DOMAIN']

    BASE_URL = os.environ['BASE_URL']
    BUCKET = os.environ['BUCKET']
    AWS_REGION = os.environ['AWS_DEFAULT_REGION']
