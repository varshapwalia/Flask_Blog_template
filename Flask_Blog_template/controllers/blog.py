from flask import Flask, render_template, redirect, current_app, request, session, g, abort, Blueprint, Response,redirect,flash
from flask_login import login_required, current_user
from flask_paginate import Pagination
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from operator import itemgetter
from dateutil import parser
import base64
import asjson

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from PIL import Image
from StringIO import StringIO
import urllib
import random
import string

# from bcrypt import hashpw, gensalt
from models.blog import *
from models.cmsuser import *
from models.comments import *
from models.contact import *

blog = Blueprint('blog', __name__)

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

def fetch_blogs():
  return BlogPost.objects(publish=True).all().order_by('-views')[:5]

def fetch_categories():
  return Categories.objects.all()

def fetch_tags():
  return BlogPost.objects.distinct('tags')

# Manage Login
@blog.route('/admin-panel',methods=["GET"])
@blog.route('/editor-panel',methods=["GET"])
def adminpanel():
  return render_template('admin/welcome.html')

@blog.route('/add_post', methods=['GET','POST'])
@login_required
def add_post():
  if request.method == 'POST':
    try:
      title = request.form["title"]
      image_url=request.form["blog_image"]
      body = request.form["body"]
      blog_url = request.form["blog_url"]
      summary=request.form["summary"]
      categories = request.form.getlist("categories[]")
      category = []
      for temp in categories: 
        temp_cat=Categories.objects(name=temp).first()
        category.append(temp_cat)
      tags = request.form.getlist("tags[]")
      awards = request.form.getlist("awards[]")
      facts = request.form.getlist("facts[]")
      temp_author=request.form["author"]
      author = Author.objects(id=temp_author).first()
      post_id = request.form['post_id']
      blog_post = None
      if post_id:
        blog_post = BlogPost.objects(id=post_id).first()
      else:
        blog_post = BlogPost(url=blog_url,title=title,summary=summary,body=body).save()
      blog_post.title=title
      blog_post.url=blog_url
      blog_post.image_url=image_url
      blog_post.body=body
      blog_post.awards=awards
      blog_post.facts=facts
      blog_post.summary=summary
      blog_post.category=category
      blog_post.tags=tags
      blog_post.author=author
      blog_post.save()
      return Response("Success")
    except Exception as e:
      return Response("Error: " + str(e))
    return Response("Some Error Occured")
  if request.method == 'GET':
    try:
      authors=Author.objects.all()
      categories = Categories.objects.all()
      return render_template('/admin/add_post.html', categories=categories,authors=authors)
    except Exception as e:
      pass
  return render_template('/admin/add_post.html', categories=[],authors=[])

@blog.route('/edit_post/<pid>', methods=['GET'])
@login_required
def edit_post(pid):
  categories = []
  old_data = []
  authors = []
  try:
    authors=Author.objects.all()
    categories = Categories.objects.all()
    old_data = BlogPost.objects(id=ObjectId(pid)).first()
  except Exception as e:
    print e
  return render_template('/admin/add_post.html', old_data=old_data, categories=categories,authors=authors)

@blog.route('/write_with_us', methods=['GET','POST'])
# @login_required
def write_with_us():
  if request.method == 'POST':
    try:
      title = request.form["title"]
      body = request.form["body"]
      user = CmsUser.objects(id=ObjectId(current_user.userid)).first()
      if title and body and user:
        WriteWithUs(title=title,body=body,user=user).save()
        return Response("Story Submitted Successfully")
      else:
        return Response("Please make sure all fields are filled.")
    except Exception as e:
      pass
    return Response("Some Error Occured. Please Try Again.")
  if request.method == 'GET':
    return render_template('/blog/write_with_us.html')

@blog.route('/all_comments', methods=['GET'])
@login_required
def all_comments():
  total = 0
  data = []
  page, per_page, offset = get_page_items()
  try:
    data = Comments.objects().order_by('-created_at')[offset:(offset+per_page)]
    total = data.count()
  except Exception as e:
    print e
  pagination = Pagination(page=page, total=total, record_name='comments', css_framework='bootstrap4',per_page=per_page)
  return render_template("/admin/comments.html", data=data, per_page=per_page, pagination=pagination) 

@blog.route('/write_with_us_list', methods=['GET'])
@login_required
def write_with_us_list():
  page, per_page, offset = get_page_items()
  data = []
  total = 0
  try:
    data = WriteWithUs.objects.all().order_by('-created_at')[offset:(offset+per_page)]
    total = data.count()
  except Exception as e:
    print e
  pagination = Pagination(page=page, total=total, record_name='users', css_framework='bootstrap4',per_page=per_page)
  return render_template("/admin/write_with_us_list.html", data=data, per_page=per_page, pagination=pagination)


@blog.route('/story_list', methods=['GET'])
# @login_required
def story_list():
  try:
    # tag_freqs = BlogPost.objects.item_frequencies('tags', normalize=True)
    # top_tags = sorted(tag_freqs.items(), key=itemgetter(1), reverse=True)[:25]
    page, per_page, offset = get_page_items()
    data = BlogPost.objects(publish=True).all().order_by('-created_at')[offset:(offset+per_page)]
    total = data.count()
    pagination = Pagination(page=page, total=total, record_name='users', css_framework='bootstrap4',per_page=per_page)
    # return render_template("/blog/blog_list.html", data=data, per_page=per_page, pagination=pagination,tags=top_tags)
    top_blogs=fetch_blogs()
    categories = fetch_categories()
    tags = fetch_tags()
    return render_template("/blog/blog_list.html", data=data, per_page=per_page, pagination=pagination,top_blogs=top_blogs,categories=categories,tags=tags)
  except Exception as e:
    print e
    return redirect('/')

@blog.route('/tag_list/<tid>', methods=['GET'])
# @login_required
def tag_list(tid):
  try:
    page, per_page, offset = get_page_items()
    data = BlogPost.objects(tags__icontains=tid,publish=True).all().order_by('-created_at')[offset:(offset+per_page)]
    total = data.count()
    pagination = Pagination(page=page, total=total, record_name='users', css_framework='bootstrap4',per_page=per_page)
    top_blogs=fetch_blogs()
    categories = fetch_categories()
    tags = fetch_tags()
    return render_template("/blog/blog_list.html", data=data, per_page=per_page, pagination=pagination, top_blogs=top_blogs,categories=categories,tags=tags)
  except Exception as e:
    print e
    return redirect('/')

@blog.route('/author/<url>', methods=['GET'])
# @login_required
def author_list(url):
  try:
    page, per_page, offset = get_page_items()
    author = Author.objects(url=url).first()
    data = BlogPost.objects(author=author, publish=True).all().order_by('-created_at')[offset:(offset+per_page)]
    total = data.count()
    pagination = Pagination(page=page, total=total, record_name='users', css_framework='bootstrap4',per_page=per_page)
    top_blogs=fetch_blogs()
    categories = fetch_categories()
    tags = fetch_tags()
    return render_template("/blog/blog_list.html", data=data, per_page=per_page, pagination=pagination, top_blogs=top_blogs,categories=categories,tags=tags)
  except Exception as e:
    print e
    return redirect('/')

@blog.route('/category_list/<name>', methods=['GET'])
# @login_required
def category_list(name):
  try:
    page, per_page, offset = get_page_items()
    category_id = Categories.objects(name=name).first()
    data = BlogPost.objects(category=category_id,publish=True).all().order_by('-created_at')[offset:(offset+per_page)]
    total = data.count()
    top_blogs=fetch_blogs()
    categories = fetch_categories()
    tags = fetch_tags()
    pagination = Pagination(page=page, total=total, record_name='users', css_framework='bootstrap4',per_page=per_page)
    return render_template("/blog/blog_list.html", data=data, per_page=per_page, pagination=pagination, top_blogs=top_blogs,categories=categories,tags=tags)
  except Exception as e:
    print e
    return redirect('/')


def upload_image(app, image_data,filename,file_format):
    conn = S3Connection(app.config['STORE_S3_ACCESS_KEY'],app.config['STORE_S3_SECRET_KEY'],host=app.config['STORE_S3_HOST'])
    bucket = conn.get_bucket(app.config['STORE_S3_BUCKET'])
    key = Key(bucket)
    key.key = filename + "."+ file_format
    key.set_contents_from_string(image_data)
    bucket.set_acl('public-read',key.key)
    return "https://%s/%s%s.%s" % (app.config['STORE_S3_HOST'], app.config['STORE_S3_BUCKET'], filename, file_format)

@blog.route('/add_image', methods=['GET','POST'])
@login_required
def add_image():
  try:
    if request.method == 'POST':
      image = request.files['pic']
      file_format = image.filename.split(".")[-1]
      filename="/production/uploaded_images/%s" % (datetime.now().strftime("%b_%d_%Y_%H_%M_%S"))
      result = upload_image(current_app,image.read(),filename,file_format)
      UploadedImage(image=result).save()
      return redirect('/add_image')
    elif request.method == 'GET':
      page, per_page, offset = get_page_items()
      data = UploadedImage.objects.all().order_by('-created_at')[offset:(offset+per_page)]
      total = data.count()
      pagination = Pagination(page=page, total=total, record_name='users', css_framework='bootstrap4',per_page=per_page)
      return render_template("/admin/add_image.html", data=data, per_page=per_page, pagination=pagination)
  except Exception as e:
    print e
    return redirect('/')

@blog.route('/delete_image', methods=['POST'])
@login_required
def delete_image():
  try:
    iid = request.form['iid']
    UploadedImage.objects(id=ObjectId(iid)).delete()
    return Response("Deleted Succesfully")
  except Exception as e:
    print e
  return Response("Some Error Occured")

@blog.route('/add_category', methods=['GET','POST'])
@login_required
def add_category():
  if request.method == 'POST':
    try:
      name = request.form['name']
      sub_category = request.form['sub_category']
      Categories(name=name,sub_category=sub_category).save()
      return redirect('/add_category')
    except Exception as e:
      print e
    return redirect('/add_category')
  if request.method == 'GET':
    page, per_page, offset = get_page_items()
    data = []
    total = 0
    try:
      data = Categories.objects.all().order_by('-created_at')[offset:(offset+per_page)]
      total = data.count()
    except Exception as e:
      print e
    pagination = Pagination(page=page, total=total, record_name='users', css_framework='bootstrap4',per_page=per_page)
    return render_template("/admin/category.html", data=data, per_page=per_page, pagination=pagination)

@blog.route('/edit_category', methods=['POST'])
@login_required
def edit_category():
  try:
    if request.method == 'POST':
      cid=request.form['cid']
      name = request.form['name']
      sub_category = request.form['sub_category']
      category = Categories.objects(id=ObjectId(cid)).first()
      category.name=name
      category.sub_category=sub_category
      category.save()
      return Response('Done')
  except Exception as e:
    print e
    return redirect('/')

@blog.route('/change_category', methods=['POST'])
@login_required
def change_category():
  try:
    if request.method == 'POST':
      cid = request.form.getlist("category")
      category = []
      for temp in cid: 
        temp_cat=Categories.objects(id=ObjectId(temp)).first()
        category.append(temp_cat)
      user = CmsUser.objects(id=ObjectId(current_user.userid)).first()
      user.category=category
      user.save()
      return redirect('/change_settings/current_user.userid')
  except Exception as e:
    pass
  return Response("Some Error Occured")

@blog.route('/subscribe', methods=['POST'])
# @login_required
def subscribe():
  try:
    if request.method == 'POST':
      email = request.form["email"]
      if not Subscribe.objects(email=email).first():
        Subscribe(email=email).save()
        return Response('You have Subscribed Successfully')
      else:
        return Response('You are already subscribed')
  except Exception as e:
    print e
  return Response("Some Error Occured")

@blog.route('/subscriber_list', methods=['GET'])
@login_required
def subscriber_list():
  try:
    data = Subscribe.objects.all()
    return render_template("/admin/subscriber_list.html", data=data)
  except Exception as e:
    print e
  return Response("Some Error Occured")

@blog.route('/add_slider', methods=['GET','POST'])
@login_required
def add_slider():
  page, per_page, offset = get_page_items()
  data = []
  total = 0
  try:
    if request.method == 'POST':
      image = request.form['image']
      head = request.form['head'] or ''
      title = request.form['title'] or ''
      link = request.form['link'] or ''
      if image:
        Slider(image=image,head=head,title=title,url=link).save()
    data = Slider.objects.order_by('-created_at')[offset:(offset+per_page)]
    total = data.count()
  except Exception as e:
    print e
  pagination = Pagination(page=page, total=total, record_name='users', css_framework='bootstrap4',per_page=per_page)
  return render_template("/admin/add_slider.html", data=data, per_page=per_page, pagination=pagination)

@blog.route('/delete_slider/<sid>', methods=['GET','POST'])
@login_required
def delete_slider(sid):
  try:
    slider = Slider.objects(id=ObjectId(sid)).first()
    if slider:
      slider.delete()
  except Exception as e:
    print e
  return redirect('/add_slider')

@blog.route('/post/<url>', methods=['GET','POST'])
# @login_required
def post(url):
  try:
    # tag_freqs = BlogPost.objects.item_frequencies('tags', normalize=True)
    # top_tags = sorted(tag_freqs.items(), key=itemgetter(1), reverse=True)[:25]
    top_blogs=fetch_blogs()
    categories = fetch_categories()
    tags = fetch_tags()
    blog=BlogPost.objects(url=url,publish=True).first()
    check = current_user.is_authenticated
    if check and blog:
      user=CmsUser.objects(id=ObjectId(current_user.userid)).first()
      favtarget=FavBlog.objects(blog=blog,user=user).first()
      if favtarget:
        status = favtarget.status
      else:
        status=False
      page, per_page, offset = get_page_items()
      data = Comments.objects(blog=blog).all().order_by('-created_at')[offset:(offset+per_page)]
      total = data.count()
      pagination = Pagination(page=page, total=total, record_name='users', css_framework='bootstrap4',per_page=per_page)
      # return render_template('/blog/single_post.html',blog=blog,comments=data,tags=top_tags,per_page=per_page,pagination=pagination,status=status)
      return render_template('/blog/single_post.html',blog=blog,comments=data,per_page=per_page,pagination=pagination,status=status, top_blogs=top_blogs,categories=categories,tags=tags)
    elif blog:
      status=False
      page, per_page, offset = get_page_items()
      data = Comments.objects(blog=blog).all().order_by('-created_at')[offset:(offset+per_page)]
      total = data.count()
      pagination = Pagination(page=page, total=total, record_name='users', css_framework='bootstrap4',per_page=per_page)
      # return render_template('/blog/single_post.html',blog=blog,comments=data,tags=top_tags,per_page=per_page,pagination=pagination,status=status)
      return render_template('/blog/single_post.html',blog=blog,comments=data,per_page=per_page,pagination=pagination,status=status, top_blogs=top_blogs,categories=categories,tags=tags)
    else:
      flash("The blog you are looking for has been Removed.")
      return redirect('/')
  except Exception as e:
    print e
    return redirect('/')

@blog.route('/remove_feature_blog/<uid>', methods=['GET','POST'])
@login_required
def remove_feature_blog(uid):
  post=BlogPost.objects(id=ObjectId(uid)).first()
  post.featured=False
  post.save()
  return redirect("/admin_post_list")

@blog.route('/feature_blog/<uid>', methods=['GET','POST'])
@login_required
def feature_blog(uid):
  try:
    BlogPost.objects(id=ObjectId(uid)).update(set__featured=True)
    return redirect("/admin_post_list")
  except Exception as e:
    return Response("%s" % str(e))
  return Response("Something Went Wrong")
  

@blog.route('/remove_publish_blog/<uid>', methods=['GET','POST'])
@login_required
def remove_publish_blog(uid):
  try:
    BlogPost.objects(id=ObjectId(uid)).update(set__publish=False)
    return redirect("/admin_post_list")
  except Exception as e:
    return Response("%s" % str(e))
  return Response("Something Went Wrong")

@blog.route('/publish_blog/<uid>', methods=['GET','POST'])
@login_required
def publish_blog(uid):
  post=BlogPost.objects(id=ObjectId(uid)).first()
  post.publish=True
  post.save()
  return redirect("/admin_post_list")

@blog.route('/add_comment', methods=['POST'])
@login_required
def add_comment():
  try:
    blog_id=request.form.get('blog_id')
    blog=BlogPost.objects(id=ObjectId(blog_id)).first()
    comment=request.form.get('comment')
    user=CmsUser.objects(id=ObjectId(current_user.userid)).first()
    Comments(blog=blog,user=user,comment=comment).save()
    return Response("Comment Added")
  except Exception as e:
    return Response("%s" % str(e))
  return Response("Something Went Wrong")

@blog.route('/add_fav', methods=['POST'])
@login_required
def add_fav():
  try:
    status=True
    blog_id=request.form.get('blog_id')
    blog=BlogPost.objects(id=ObjectId(blog_id)).first()
    user=CmsUser.objects(id=ObjectId(current_user.userid)).first()
    temp_check = FavBlog.objects(blog=blog,user=user).first()
    if temp_check:
      temp_check.status = status
      temp_check.save()
      return Response("Favourite Already exist")
    FavBlog(blog=blog,user=user,status=status).save()
    return Response("Favourite Added")
  except Exception as e:
    return Response("%s" % str(e))
  return Response("Something Went Wrong")

@blog.route('/remove_fav', methods=['POST'])
@login_required
def remove_fav():
  try:
    blog_id=request.form.get('blog_id')
    user=CmsUser.objects(id=ObjectId(current_user.userid)).first()
    blog=BlogPost.objects(id=ObjectId(blog_id)).first()
    fav_blog = FavBlog.objects(blog=blog,user=user).first()
    if fav_blog:
      fav_blog.status=False
      fav_blog.save()
      return Response("Favourite Removed")
    return Response("Could not find Blog")
  except Exception as e:
    return Response("%s" % str(e))
  return Response("Something Went Wrong")

@blog.route('/add_view', methods=['POST'])
# @login_required
def add_view():
  try:
    blog_id=request.form.get('blog_id')
    BlogPost.objects(id=ObjectId(blog_id)).update_one(inc__views=1)
    return Response("Comment Added")
  except Exception as e:
    return Response("%s" % str(e))
  return Response("Something Went Wrong")

@blog.route('/admin_post_list', methods=['GET'])
@login_required
def admin_post_list():
  data = []
  total = 0
  try:
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
    if search:
      query['$or'] = [{'title':{'$regex':q, '$options': 'i'}},{'tags':{'$regex':q, '$options': 'i'}}]
      data = BlogPost.objects(__raw__=(query)).order_by('-created_at')[offset:(offset+per_page)]
    else:
      data = BlogPost.objects(__raw__=(query)).order_by('-created_at')[offset:(offset+per_page)]
    total = data.count()
  except Exception as e:
    pass
  pagination = Pagination(page=page, total=total, record_name='users', css_framework='bootstrap4',per_page=per_page)
  return render_template("/admin/admin_post_list.html", data=data, per_page=per_page, pagination=pagination, query=request.args.to_dict())

@blog.route('/delete_post', methods=['POST'])
@login_required
def delete_post():
  try:
    pid=request.form['pid']
    post=BlogPost.objects(id=ObjectId(pid)).first()
    post.delete()
    return Response("Post Deleted")
  except Exception as e:
    print e
  return Response("Something Went Wrong")

@blog.route('/add_author', methods=['GET','POST'])
@login_required
def add_author():
  authors = Author.objects.all()
  try:
    if request.method == 'POST':
      name=request.form["name"]
      description=request.form["description"]
      url=request.form["url"]
      Author(name=name,description=description,url=url).save()
      return Response("Successfully Added")
    elif request.method == "GET":
      return render_template("/admin/add_author.html",authors=authors)
  except Exception as e:
    print e
  return render_template("/admin/add_author.html",authors=authors)
