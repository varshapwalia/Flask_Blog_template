import os, sys
sys.path.insert(0,'..')

from flask import Flask
from flask_mongoengine import MongoEngine
from bcrypt import hashpw, gensalt

from models.cmsuser import *
from models.blog import *

app = Flask(__name__)
app.config.from_object('config.ProductionConfig')
# app.config.from_object('config.DevelopmentConfig')

# Connnect with mongodb
# Mongodb Settings are there in APP_SETTINGS
db = MongoEngine(app)

def get_password(password):
    """ convert password string into hash """
    return hashpw(password.encode('utf-8'), gensalt())

# Drop users database
def drop_user_database():
  CmsUserRole.drop_collection()
  CmsUser.drop_collection()
  CmsUserLog.drop_collection()
  return "Done"

def add_author():
  author = Author.objects(url="team-drilers").first()
  BlogPost.objects.update(set__author=author)
  return "Done"


def insert_user_database():
  # Create Roles
  dataentryRole = CmsUserRole(name="editor").save()
  adminRole = CmsUserRole(name="admin").save()
  # investorRole = CmsUserRole(name="investor").save()
  # Create CMS Users
  CmsUser(full_name="Testy Tester",email="test2@gmail.com",password=get_password("password"),userrole=adminRole).save()
  return "Done"

def insert_new_role():
  investorRole = CmsUserRole(name="investor").save()
  return "Done"


if __name__ == "__main__":
  # drop_user_database()
  # insert_user_database()
  add_author()
  # insert_new_role()