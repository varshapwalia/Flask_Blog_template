""" Database models for the CMS user """

from flask_mongoengine import MongoEngine
from base import BaseDocument
import logging
import blog

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

db = MongoEngine()

class CmsUser(BaseDocument):
    """ A CmsUser model defining some fields

    :param email email: Email or username of CMS User
    :param string mobile: Mobile number 
    :param string password: Encrypted password
    :param string fullname: Full name of user
    :param string auth_token: Authorization Token required each time user make call to services
    :param datetime last_logged_in: Last Login time of user
    :param reference userrole: Role of user selected from all roles
    :param reference userlog: List of sessions when user logged in

    """
    email = db.EmailField(unique=True,required=True)
    mobile = db.StringField()
    category = db.ListField(db.ReferenceField('Categories'))
    password = db.StringField(required=True) 
    full_name = db.StringField() # Should be required
    auth_token = db.StringField()
    last_logged_in = db.DateTimeField()
    userrole = db.ReferenceField('CmsUserRole')
    userlog = db.ListField(db.ReferenceField('CmsUserLog'))
    block = db.BooleanField(default=False)
    meta = {'indexes':['email','auth_token']}

    def to_json1(self):
        """Return CmsUser class data in JSON format"""
        return {"id":str(self.id),"email":self.email,"mobile":self.mobile,"name":self.full_name}

class CmsUserLog(BaseDocument):
    """A CmsUserLog class defining some fields
    
    :param reference user: Admin panel user reference
    :param datetime login_time: Date and time of user login to the admin panel
    :param list_of_string user_activity: user activity during the session
    :param datetime logout_time: Date and time of user logged out of the admin panel
   
    """
    user = db.ReferenceField('CmsUser')
    login_time = db.DateTimeField()
    user_activity = db.ListField(db.StringField())
    logout_time = db.DateTimeField()

class CmsUserRole(BaseDocument):
    """A CmsUserRole class defining some fields
    
    :param string name: Name of Role
    :param string desc: Description of Role
    :param list_of_string allowed: Allowed Permissions to the user
   
    """
    name = db.StringField(required=True)
    desc = db.StringField()
    allowed = db.ListField(db.StringField())

def get_user_role(name='user'):
    role = CmsUserRole.objects(name=name).first()
    if not role:
        role = CmsUserRole(name=name).save()
    return role

# OTP
class Otp(BaseDocument):

    email = db.StringField(unique=True)
    otp = db.StringField(default="12345")
    expired_at = db.DateTimeField()
    sent = db.BooleanField(default=False)
    verification = db.BooleanField(default=False)

class EmailValidator(BaseDocument):
  email = db.EmailField(unique=True)
  valid = db.BooleanField(default=False)
  tries = db.IntField(default=0)

def get_email_validator(email):
  ev = EmailValidator.objects(email=email).first()
  if not ev:
    ev = EmailValidator(email=email).save()
  return ev