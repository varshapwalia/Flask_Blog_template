from flask import Flask, render_template, redirect, current_app, request, session, g, abort, Blueprint, Response, flash
from flask_login import login_required, current_user
from flask_paginate import Pagination
from bson.objectid import ObjectId
from bcrypt import hashpw, gensalt
import asjson
import json,requests
from datetime import datetime, timedelta
import string

# from bcrypt import hashpw, gensalt
from models.cmsuser import *
from models.comments import *

users = Blueprint('users', __name__)

def get_page_items():
    """ calculate offset according to page number """

    page = int(request.args.get('page', 1))
    per_page = request.args.get('per_page')
    if not per_page:
        per_page = 10
    else:
        per_page = int(per_page)
    offset = (page - 1) * per_page
    return page, per_page, offset

@users.route('/users', methods=['GET'])
@login_required
def users_list():

    q = request.args.get('q', default=None)
    if q:
        search = True
    else:
        search = False
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    page, per_page, offset = get_page_items()
    query = {}
    # User Type
    role = CmsUserRole.objects(name__in=["user","editor"]).all()
    if search:
        query['$or'] = [{'full_name':{'$regex':q, '$options': 'i'}},{'email':{'$regex':q, '$options': 'i'}},{'mobile':{'$regex':q, '$options': 'i'}}]
        data = CmsUser.objects(__raw__=(query),userrole__in=role).order_by('-created_at')[offset:(offset+per_page)]
    else:
        data = CmsUser.objects(__raw__=(query),userrole__in=role).order_by('-created_at')[offset:(offset+per_page)]
    total = data.count()
    pagination = Pagination(page=page, total=total, record_name='users', css_framework='bootstrap4',per_page=per_page)
    return render_template("/admin/users_list.html", data=data, per_page=per_page, pagination=pagination, query=request.args.to_dict())

def check_password(password, actual_password):
    """ check password from database with hashing """
    if password and actual_password:
        return hashpw(password.encode('utf-8'), actual_password.encode('utf-8')) == actual_password
    else:
        return False

def get_password(password):
    """ convert password string into hash """
    return hashpw(password.encode('utf-8'), gensalt())

@users.route('/unblock_user/<uid>', methods=['GET','POST'])
@login_required
def unblock_user(uid):
	user=CmsUser.objects(id=ObjectId(uid)).first()
	user.block=False
	user.save()
	return redirect("/users")

@users.route('/block_user/<uid>', methods=['GET','POST'])
@login_required
def block_user(uid):
	user=CmsUser.objects(id=ObjectId(uid)).first()
	user.block=True
	user.save()
	return redirect("/users")

@users.route('/change_settings/<uid>', methods=['GET','POST'])
@login_required
def change_settings(uid):
    if request.method == 'POST':
        try:
            old_password = request.form["old_password"]
            new_password=request.form["new_password"]
            confirm_password=request.form["confirm_password"]
            user=CmsUser.objects(id=ObjectId(uid)).first()
            check = check_password(old_password, user.password)
            if check:
                if new_password==confirm_password:
                    next_password=get_password(new_password)
                    user.password=next_password
                    user.save()
                    return Response("Password Updated Succesfully")
                else:
                    return Response("New password do not match confirm password")
            else:
                return Response("Your old password do not match")
        except Exception as e:
            print e
        return Response("Unable to change password. Please Try Again.")
    if request.method == 'GET':
        try:
            data = Categories.objects.all()
            return render_template('/user/change_password.html',data=data)
        except Exception as e:
            pass
        return render_template('/user/change_password.html',data=[])
        

@users.route('/comments/<uid>', methods=['GET'])
@login_required
def comments(uid):
    page, per_page, offset = get_page_items()
    data = []
    total = 0
    try:
        user = CmsUser.objects(id=ObjectId(uid)).first()
        data = Comments.objects(user=user).order_by('-created_at')[offset:(offset+per_page)]
        total = data.count()
    except Exception as e:
        print e
    pagination = Pagination(page=page, total=total, record_name='comments', css_framework='bootstrap4',per_page=per_page)
    return render_template("/user/comments.html", data=data, per_page=per_page, pagination=pagination)

@users.route('/delete_comment', methods=['POST'])
@login_required
def delete_comment():
    try:
        pid=request.form['pid']
        post=Comments.objects(id=ObjectId(pid)).first()
        post.delete()
        return Response("Comment Deleted")
    except Exception as e:
        print e
        return redirect('/')

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

@users.route('/add_editor', methods=['GET','POST'])
@login_required
def add_editor():
    if request.method == 'POST':
        try:
            email=request.form['email']
            name=request.form['name']
            mobile=request.form['mobile']
            password=request.form['pass']
            cnames = request.form.getlist("categories")
            category = []
            for temp in cnames: 
                temp_cat=Categories.objects(name=temp).first()
                if temp_cat:
                    category.append(temp_cat)
            confirm_password=request.form['confirm_pass']
            role = CmsUserRole.objects(name="editor").first()
            user=CmsUser.objects(email=email).first()
            if not role:
                CmsUserRole(name="editor").save()
            # if not validate_email_api(current_app, email):
            #     return Response("Not a valid email id")
            if user:
                return Response("User Already Exist")
            if password != confirm_password:
                return Response("Password Does not match")
            CmsUser(full_name=name,email=email,password=get_password(password),mobile=mobile,category=category,userrole=role).save()
            return Response("Editor Succesfully Added")
        except Exception as e:
            pass
        return Response("Some Error Occured. Please Try Again.")
    elif request.method == 'GET':
        data = Categories.objects.all()
        return render_template("/admin/add_editor.html", data=data)

@users.route('/edit_comment', methods=['POST'])
@login_required
def edit_comment():
    try:
        cid=request.form['cid']
        comment=request.form['comment']
        post=Comments.objects(id=ObjectId(cid)).first()
        post.comment=comment
        post.save()
        return Response("Comment Deleted")
    except Exception as e:
        print e
        return redirect('/')

def otp_generator(size=6, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@users.route('/forgot_password', methods=['GET','POST'])
# @login_required
def forgot_password():
    try:
        if request.method == 'POST':
            email=request.form['email']
            user=CmsUser.objects(email=email).first()
            if not user:
                flash("User Does not exist. Please Signup!.")
                return redirect("/register")
            else:
                otp_obj = Otp.objects(email=email).first()
                if not otp_obj:
                    otp_obj = Otp(email=email,expired_at=datetime.now()).save()
                if (otp_obj.expired_at>datetime.now() and otp_obj.sent and otp_obj.verification==False) or (otp_obj.expired_at<datetime.now() and otp_obj.sent and otp_obj.verification==True):
                    flash("OTP was Sent Already. You can resend otp after 5 min. Please Check the Spam folder.")
                    return redirect("/verify_otp?email=%s"% email)
                elif (otp_obj.expired_at<datetime.now() and otp_obj.verification==False) or (otp_obj.expired_at<datetime.now() and otp_obj.verification==True):
                    otp_obj.expired_at=datetime.now()+timedelta(minutes=5)
                    otp_obj.sent=True
                    # otp_obj.otp=otp_generator()
                    otp_obj.save()
                    # data = {"to": email,"otp":otp_obj.otp,"email_type": "verify"}
                    # push_thoonk(current_app, 'email', data) # Sending OTP
                    flash("OTP is Sent on email. It will expire in 5 minutes. Please Check the Spam folder.")
                    return redirect("/verify_otp?email=%s"% email)
        elif request.method == 'GET':
            return render_template("/user/forgot_password.html")
    except Exception as e:
        print e
        return redirect('/')

@users.route('/verify_otp', methods=['GET','POST'])
# @login_required
def verify_otp():
    try:
        if request.method == 'POST':
            email=request.form['email']
            otp=request.form['otp']
            password=request.form['password']
            confirm_password=request.form['confirm_password']
            user=CmsUser.objects(email=email).first()
            otp_obj= Otp.objects(email=email).first()
            if password!=confirm_password:
                flash("Password do not match")
                return redirect("/forgot_password")
            elif otp_obj.otp!=otp and otp_obj.otp=="verfified":
                flash("OTP was incorrect or expired. Pleasetry again!")
                return redirect("/verify_otp?email=%s"% email)
            elif user and (otp_obj.otp==otp):
                otp_obj.sent=False
                otp_obj.verification==False
                otp_obj.expired_at=datetime.now()
                otp_obj.save()
                user.password=get_password(password)
                user.save()
                return redirect("/login")
            else:
                flash("User Does not exist. Please Signup!.")
                return redirect("/register")
        elif request.method == 'GET':
            email=request.args['email']
            return render_template("/user/verify_otp.html",email=email)
    except Exception as e:
        print e
        return redirect('/')

@users.route('/fav_blogs', methods=['GET'])
@login_required
def fav_blogs():
    page, per_page, offset = get_page_items()
    total = 0
    data = []
    try:
        user=CmsUser.objects(id=ObjectId(current_user.userid)).first()
        data = FavBlog.objects(user=user,status=True).all().order_by('-created_at')[offset:(offset+per_page)]
        total = data.count()
    except Exception as e:
        pass
    pagination = Pagination(page=page, total=total, record_name='blogs', css_framework='bootstrap4',per_page=per_page)
    return render_template("/user/favblog.html", data=data, per_page=per_page, pagination=pagination) 
