#!/usr/bin/python
import sys
sys.path.insert(0,'..')

from flask import Flask
from threading import Thread
from flask_mail import Mail, Message
from flask_mongoengine import MongoEngine
import thoonk

from models.templates import *

app = Flask(__name__)
app.config.from_object('config.ProductionConfig')
# app.config.from_object('config.DevelopmentConfig')

# Connnect with mongodb
# Mongodb Settings are there in APP_SETTINGS
db = MongoEngine(app)

# Flask mail client
mail=Mail(app)

def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target = f, args = args, kwargs = kwargs)
        thr.start()
    return wrapper

@async
def send_async_email(msg):
    with app.app_context():
        mail.send(msg)

def init():
    """ Triggered while sending Email """
    ps = thoonk.Pubsub()
    q = ps.pyqueue('email')
    while True:
        try:
            value = q.get()
            mail_to = value['to']
            otp = value['otp']
            email_type = value['email_type']
            if email_type == "verify":
                subject = "Drifter-Please verify your account!"
                body = "<p>Your OTP is %s.</p>" % otp 
                msg = Message(subject,sender=('Team Drilers', 'support@drilers.com'),recipients=[mail_to])
                msg.html = body
                send_async_email(msg)
        except Exception, e:
            pass
    ps.close()
    return

if __name__ == "__main__":
    init()