""" Database models for the CMS user """

from flask_mongoengine import MongoEngine
from base import BaseDocument

db = MongoEngine()

class ContactUs(BaseDocument):

    name=db.StringField(required=True)
    title=db.StringField()
    mobile=db.StringField()
    email=db.StringField()
    body=db.StringField()
    meta = {'indexes':['name']}

class Subscribe(BaseDocument):
  
    email=db.StringField(required=True,unique=True)
    meta = {'indexes':['email']}
  
    
