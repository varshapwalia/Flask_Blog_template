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

Author(name="Team Drilers", url="team-drilers", description="Team Drilers").save()
Author(name="Megha", url="megha", description="").save()

editorRole = CmsUserRole(name="editor").save()
adminRole = CmsUserRole(name="admin").save()

CmsUser(email="drilers.content@gmail.com", mobile="9619688167", full_name="Drilers Content", password=get_password("Drilersinfo@123#"),userrole=editorRole).save()
CmsUser(email="drilersinfo@gmail.com", mobile="9467470747", full_name="Team Drilers", password=get_password("Drilersinfo@123#"),userrole=adminRole).save()
CmsUser(email="rajanambala007@gmail.com", mobile="9467470747", full_name="Rajan Sahni", password=get_password("Drilersinfo@123#"),userrole=adminRole).save()


Categories(name="Motivational Stories", url="motivational-stories").save()
Categories(name="Rising Women Stories", url="rising-women-stories").save()
Categories(name="Truly Inspiring Stories", url="truly-inspiring-stories").save()
Categories(name="Entrepreneurial Success Stories", url="entrepreneurial-success-stories").save()
Categories(name="Sports Inspirational Stories", url="sports-inspirational-stories").save()
Categories(name="Inspiring Stories", url="inspiring-stories").save()
Categories(name="Rags to riches in India", url="rags-to-riches-in-india").save()
Categories(name="Art", url="art").save()
Categories(name="Music", url="music").save()
Categories(name="Lifestyle", url="lifestyle").save()