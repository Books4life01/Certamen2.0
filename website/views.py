from flask import Blueprint, render_template, flash, request, redirect, url_for

views = Blueprint('views', __name__)#passing the name of the blueprint and the name of the file

@views.route('/')#this is the route for the home page
def home():
    return render_template("home/base.html")
@views.route('/error')
def error():
    flash(str(request.args.get('msg')))
    return render_template("util/error.html")
