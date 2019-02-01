""" Database models for the CMS user """

from flask_mongoengine import MongoEngine
from base import BaseDocument
from cmsuser import *

db = MongoEngine()

class BlogPost(BaseDocument):
    title = db.StringField(unique=True,required=True)
    url = db.StringField(unique=True,required=True)    
    summary = db.StringField(required=True)
    image_url = db.StringField()
    category = db.ListField(db.ReferenceField('Categories'))
    awards = db.ListField(db.StringField())
    facts = db.ListField(db.StringField())
    body = db.StringField(required=True)
    featured = db.BooleanField(default=False)
    publish = db.BooleanField(default=True)
    author = db.ReferenceField('Author')
    tags = db.ListField(db.StringField())
    views = db.IntField(default=0)
    likes = db.ReferenceField('CmsUser')
    likes_count = db.IntField(default=0)

    meta = {
        'indexes': ['title']
    }

class Author(BaseDocument):
    name = db.StringField()
    url = db.StringField(unique=True, required=True)
    description = db.StringField()

    meta = {'indexes':['url']}

class WriteWithUs(BaseDocument):
    title = db.StringField(required=True)
    body = db.StringField(required=True)
    user = db.ReferenceField('CmsUser')
    
    meta = {'indexes':['title']}

# Need to Remove Sub Category
class Categories(BaseDocument):
    name = db.StringField(required=True,unique=True)
    sub_category = db.StringField()
    url = db.StringField()
    
    meta = {'indexes':['name']}

class UploadedImage(BaseDocument):
    image = db.StringField(unique=True,required=True)

    meta = {'indexes':['image']}

class Slider(BaseDocument):
    image = db.StringField(unique=True,required=True)
    head = db.StringField()
    title = db.StringField()
    url = db.StringField()

    meta = {'indexes':['image']}

class FavBlog(BaseDocument):
    blog=db.ReferenceField('BlogPost')
    user=db.ReferenceField('CmsUser')
    status=db.BooleanField(default=False)
    meta = {'indexes':['blog']}

class ContactUs(BaseDocument):
    name = db.StringField(required=True)
    title = db.StringField()
    mobile = db.StringField()
    email = db.StringField()
    body = db.StringField()

    meta = {'indexes':['name']}
