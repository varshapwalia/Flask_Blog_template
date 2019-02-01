from flask import Flask, render_template, redirect, current_app, request, session, g, abort, Blueprint, Response,flash
from flask_login import login_required, current_user
from operator import itemgetter
from flask_paginate import Pagination
import asjson

# from bcrypt import hashpw, gensalt
from models.blog import *
from models.contact import *

main = Blueprint('main', __name__)


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

# def top_categories(limit=3):
#   category_freqs = BlogPost.objects.item_frequencies('category')
#   return sorted(category_freqs.items(), key=itemgetter(1), reverse=True)[:limit]

# def category_blogs(category_id=None, limit=3, offset=0):
#   category = Categories.objects(id=category_id).first()
#   if category:
#     posts = BlogPost.objects(category=category, publish=True).all()
#     return category.name, posts[offset:limit] if limit else posts
#   return None, []


@main.route('/')
# @login_required
def index():
	# BlogPost.drop_collection()
	# CmsUser.drop_collection()
	featured=BlogPost.objects(featured=True,publish=True).all()
	# tag_freqs = BlogPost.objects.item_frequencies('tags', normalize=True)
	# top_tags = sorted(tag_freqs.items(), key=itemgetter(1), reverse=True)[:25]
	slider = Slider.objects.all()
	# return render_template('/blog/homepage.html',tags=top_tags,top_blogs=top_blogs,featured=featured,slider=slider)
	# categories = top_categories()
	# categories_dict = {}
	# for cat in categories:
	# 	name, blogs = category_blogs(cat[0])
	# 	categories_dict[name] = blogs
	# return render_template('/blog/homepage.html',top_blogs=top_blogs,featured=featured,slider=slider, categories_dict=categories_dict)
	top_blogs=fetch_blogs()
	categories = fetch_categories()
	tags = fetch_tags()
	return render_template('/blog/homepage.html',top_blogs=top_blogs,featured=featured,slider=slider,categories=categories,tags=tags)

@main.route('/search', methods=["GET","POST"])
# @login_required
def search():
	try:
		q=request.form['search']
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
			data = BlogPost.objects(__raw__=(query),publish=True).order_by('-created_at')[offset:(offset+per_page)]
		else:
			data = BlogPost.objects(__raw__=(query),publish=True).order_by('-created_at')[offset:(offset+per_page)]
		total = data.count()
		top_blogs=fetch_blogs()
		categories = fetch_categories()
		tags = fetch_tags()
		pagination = Pagination(page=page, total=total, record_name='users', css_framework='bootstrap4',per_page=per_page)
		if total>=1:
			return render_template("/blog/blog_list.html", data=data, per_page=per_page, pagination=pagination, top_blogs=top_blogs,categories=categories,tags=tags, query=request.args.to_dict())
		else:
			flash("No result found! Please try again for different search word or read from our current collection.")
			return render_template('/blog/blog_list.html',pagination=pagination,top_blogs=top_blogs,categories=categories,tags=tags)

	except Exception as e:
		print e
		return redirect('/')

@main.route('/about_us')
# @login_required
def about_us():
	top_blogs=BlogPost.objects(publish=True).all().order_by('-views')[:5]
	categories = Categories.objects.all()
	return render_template('/blog/about_us.html',top_blogs=top_blogs,categories=categories)

@main.route('/terms-and-conditions')
# @login_required
def terms_and_conditions():
	return render_template('/blog/terms-and-conditions.html')

@main.route('/privacy-policy')
# @login_required
def privacy_policy():
	return render_template('/blog/privacy-policy.html')

@main.route('/disclaimer')
# @login_required
def disclaimer():
	return render_template('/blog/disclaimer.html')	
