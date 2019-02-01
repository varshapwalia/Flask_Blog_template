import os, sys
sys.path.insert(0,'..')

from flask import Flask
from flask_mongoengine import MongoEngine
from bcrypt import hashpw, gensalt

from models.blog import *

app = Flask(__name__)
# app.config.from_object('config.ProductionConfig')
app.config.from_object('config.DevelopmentConfig')

# Connnect with mongodb
# Mongodb Settings are there in APP_SETTINGS
db = MongoEngine(app)

def publish_blog():
  blogs = BlogPost.objects.all()
  for blog in blogs:
    print blog.publish


if __name__ == "__main__":
  publish_blog()
