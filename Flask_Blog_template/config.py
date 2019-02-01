import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
  DEBUG = False
  TESTING = False
  CSRF_ENABLED = True
  SECRET_KEY = 'thisissecret'

class DevelopmentConfig(Config):
  DEVELOPMENT = True
  DEBUG = True
  BASE_URL = 'http://localhost:5000/'
  # MongoDB
  MONGODB_DB = 'drilers'
  MONGODB_USERNAME = 'db_driler' #db_driler
  MONGODB_PASSWORD = 'put_password_here'
  MONGODB_HOST = 'put shard connection here'
  # GOOGLE_API_KEY = 'AIzaSyDWZwgFwCc4zIRh9EROaPldPHBXHe_zvoQ'
  STORE_S3_BUCKET = 'drilersblog'
  STORE_S3_HOST = 's3.ap-south-1.amazonaws.com'
  STORE_S3_URL = 'https://s3.ap-south-1.amazonaws.com/drilersblog/'
  STORE_S3_ACCESS_KEY = 'your_access_key'
  STORE_S3_SECRET_KEY = 'your_secret_key'
  ZERO_BOUNCE_API_KEY = 'email_verifying_key'
  ZERO_BOUNCE_URL = "https://api.zerobounce.net/v1/validate"

class ProductionConfig(Config):
  DEBUG = False
  DEVELOPMENT = False
  # SECRET_KEY = 'kalyanikhona%$#@!'
  BASE_URL = 'http://test.drilers.in/'
  # BASE_URL = 'http://driler-demo.herokuapp.com'
  MONGODB_DB = 'drilers'
  MONGODB_USERNAME = 'db_driler' #db_driler
  MONGODB_PASSWORD = 'put_password_here'
  MONGODB_HOST = 'put shard connection here'
  # GOOGLE_API_KEY = 'AIzaSyDWZwgFwCc4zIRh9EROaPldPHBXHe_zvoQ'
  STORE_S3_BUCKET = 'drilersblog'
  STORE_S3_HOST = 's3.ap-south-1.amazonaws.com'
  STORE_S3_URL = 'https://s3.ap-south-1.amazonaws.com/drilersblog/'
  STORE_S3_ACCESS_KEY = 'your_access_key'
  STORE_S3_SECRET_KEY = 'your_secret_key'
  ZERO_BOUNCE_API_KEY = 'email_verifying_key'
  ZERO_BOUNCE_URL = "https://api.zerobounce.net/v1/validate"
