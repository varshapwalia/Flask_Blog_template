import os
from flask import Flask,render_template, redirect, current_app, request, session, g, abort, Blueprint,flash,Response
from bson.objectid import ObjectId
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_principal import Principal, Identity, AnonymousIdentity, identity_changed, identity_loaded, RoleNeed, UserNeed, Permission
from flask_mongoengine import MongoEngine
from flask_cors import CORS
import requests
import json

# Extra packages
from datetime import datetime, timedelta
from bcrypt import hashpw, gensalt

from forms import LoginForm

from controllers.main import main
from controllers.blog import blog
from controllers.users import users
from controllers.contact import contact

app = Flask(__name__)
CORS(app)

app.config.from_object('config.ProductionConfig')
# app.config.from_object('config.DevelopmentConfig')

db = MongoEngine(app)

# login user
login_manager = LoginManager()
principals = Principal(app)
login_manager.init_app(app)
login_manager.login_view = "login"

app.register_blueprint(main)
app.register_blueprint(blog)
app.register_blueprint(users)
app.register_blueprint(contact)

from models.cmsuser import *
from models.blog import *

# Loading user data for authentication
@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    """ loading user data after logged in """
    # Set the identity user object
    identity.user = current_user
    # Add the UserNeed to the identity
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))
    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    if hasattr(current_user, 'roles'):
        for role in current_user.roles:
            identity.provides.add(RoleNeed(role))

class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])


# Creating user session
class SessionUser():
    """ Creating Session for Logged in user """
    def __init__(self, userid=None, username=None, password=None, roles=None, role_name=None, block=False):
        self.userid = userid
        self.username = username
        self.password = password
        self.roles = roles
        self.role_name = role_name
        self.block = block
        try:
            self.userlog_id = session['userlog_id']
        except Exception as e:
            self.userlog_id = None
    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def is_block(self):
        return self.block
    def get_id(self):
        return unicode(self.userid)
    def get_userlog_id(self):
        return unicode(self.userlog_id)
    def __repr__(self):
        return '<User %r>' % self.username
    def check_password(self,password):
        return hashpw(password.encode('utf-8'),self.password.encode('utf-8'))==self.password

# Loading user data
@login_manager.user_loader
def load_user(userid):
    """ Loading user data from database """
    # Return an instance of the User model
    user = CmsUser.objects(id=userid).first()
    if user and (not user.block):
        return SessionUser(userid=str(user.id),username=user.email,password=user.password, roles=user.userrole.allowed, role_name=user.userrole.name, block = user.block)
    return None

# Fetching user from database
def get_user_by_email(email):
    """ Loading user data from database using email address """
    user = CmsUser.objects(email=email.lower()).first()
    if user:
        return SessionUser(userid=str(user.id),username=user.email,password=user.password, roles=user.userrole.allowed, role_name = user.userrole.name, block = user.block)
    return None

# Manage Login
@app.route('/login',methods=["GET","POST"])
def login():
    """ Login User """
    if request.method == 'POST':
        try:
            user = get_user_by_email(request.form['email'])
            # Compare passwords (use password hashing production)
            if user and (not user.is_block()):
                if user.check_password(request.form['password']):
                    # Keep the user info in the session using Flask-Login
                    cmsuser = CmsUser.objects(id=user.get_id()).first()
                    userlog = CmsUserLog(user=cmsuser,login_time=datetime.now()).save()
                    cmsuser.userlog.append(userlog)
                    cmsuser.save()
                    session['userlog_id'] = str(userlog.id)
                    login_user(user)
                    # Tell Flask-Principal the identity changed
                    identity_changed.send(current_app._get_current_object(), identity=Identity(user.get_id()))
                    return Response("Success")
            elif user and user.is_block():
                return Response('You are not allowed to use this panel. Please Contact Admin for more details.')
            return Response("Wrong Email or Password")
        except Exception as e:
            pass
        return Response("Some Error Occured while loggin in. Please Try Again.")
    if request.method == 'GET':
        return render_template('blog/login.html')

# Manage Logout
@app.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    """ Logout User and destroy its session """
    # Remove the user information from the session
    userlog = CmsUserLog.objects.filter(id=current_user.get_userlog_id()).first()
    userlog.logout_time = datetime.now()
    userlog.save()
    logout_user()
    # Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)
    # Tell Flask-Principal the user is anonymous
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
    return redirect(app.config['BASE_URL'])

def get_password(password):
    """ convert password string into hash """
    return hashpw(password.encode('utf-8'), gensalt())

def validate_email_api(app, email):
    # if app.config['DEVELOPMENT']:
    #     return True
    ev = get_email_validator(email)
    if ev.valid:
        return True 
    elif (ev.tries and ev.tries%3 == 0 and (timedelta(minutes=10) > (datetime.now() - ev.updated_at))):
        return False
    else:
        # ZERO BOUNCE API to validate Email Addresses
        ZERO_BOUNCE_API_KEY = app.config["ZERO_BOUNCE_API_KEY"]
        ZERO_BOUNCE_URL = app.config["ZERO_BOUNCE_URL"]
        email_response = requests.get(ZERO_BOUNCE_URL, params={"email": email, "apikey": ZERO_BOUNCE_API_KEY})
        json_data = json.loads(email_response.text or {})
        ev.valid = (json_data['status'] == "Valid")
        ev.tries = ev.tries + 1
        ev.save()
        return (json_data['status'] == "Valid")
    return False

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            email = request.form['email']
            user = CmsUser.objects(email=email).first()
            if user:
                return Response("Email Address already registered")
            name = request.form['name']
            mobile = request.form['mobile']
            password = request.form['password']
            # confirm_password = request.form['confirm_password']
            categories = request.form.getlist("categories[]")
            print categories
            category = []
            for temp in categories: 
                temp_cat = Categories.objects(name=temp).first()
                category.append(temp_cat)
            role = get_user_role("user")
            if not validate_email_api(current_app, email):
                return Response('Email is Invalid!! Please try a valid email id.')
            CmsUser(full_name=name,email=email,password=get_password(password),userrole=role, category=category,mobile=mobile).save()
            return Response("Success")
        except Exception as e:
            pass
        return Response("Error Occurred while registering. Please Try again.")
    elif request.method == 'GET':
        try:
            categories = Categories.objects.all()
            return render_template('blog/register.html', categories=categories)
        except Exception as e:
            pass
        return render_template('blog/register.html', categories=[])


@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return redirect(app.config['BASE_URL'] + 'login')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)