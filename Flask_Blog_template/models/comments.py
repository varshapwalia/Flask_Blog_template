""" Database models for the CMS user """

from flask_mongoengine import MongoEngine
from base import BaseDocument

from blog import *
from cmsuser import *

db = MongoEngine()

class Comments(BaseDocument):
  blog = db.ReferenceField('BlogPost')
  user = db.ReferenceField('CmsUser')
  comment = db.StringField(required=True)

  meta = {'indexes':['comment']}