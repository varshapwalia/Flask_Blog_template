from flask import Flask, render_template, redirect, current_app, request, session, g, abort, Blueprint, Response,flash
from flask_login import login_required, current_user
from flask_paginate import Pagination
from bson.objectid import ObjectId
from operator import itemgetter
import asjson

# from bcrypt import hashpw, gensalt
from models.contact import *
from models.cmsuser import *

contact = Blueprint('contact', __name__)


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


@contact.route('/contact_us', methods=['GET','POST'])
# @login_required
def contact_us():
  if request.method == 'POST':
    try:
      name = request.form["name"] or ""
      title = request.form["title"] or ""
      email = request.form["email"] or ""
      mobile = request.form["mobile"] or ""
      body = request.form["details"] or ""
      ContactUs(name=name, title=title, email=email, mobile=mobile, body=body).save()
      return Response("Successfully Submitted")
    except Exception as e:
      print e
    return Response("Some Error Occured. Please Try again.")
  if request.method == 'GET':
    try:
      user = CmsUser.objects(id=ObjectId(current_user.userid)).first()
      if user:
        return render_template('/blog/contact_us.html', user=user)
    except Exception as e:
      pass
    return render_template('/blog/contact_us.html')

@contact.route('/feedback', methods=['POST'])
# @login_required
def feedback():
  try:
    if request.method == 'POST':
      requests = request.form
      name = request.form["name"] or ""
      title = request.form["title"] or ""
      email = request.form["email"] or ""
      mobile = request.form["mobile"] or ""
      body = request.form["details"] or ""
      ContactUs(name=name, title=title, email=email, mobile=mobile, body=body).save()
      return Response("Feedback Sent Successfully!")
  except Exception as e:
    pass
  return Response("Something Went Wrong. Please Try Again.")

@contact.route('/contact_list', methods=['GET','POST'])
@login_required
def contact_list():
  page, per_page, offset = get_page_items()
  data = []
  total = 0
  try:
    data = ContactUs.objects.all().order_by('-created_at')[offset:(offset+per_page)]
    total = data.count()
  except Exception as e:
    print str(e)
  pagination = Pagination(page=page, total=total, record_name='users', css_framework='bootstrap4',per_page=per_page)
  return render_template("/admin/contact_list.html", data=data, per_page=per_page, pagination=pagination)