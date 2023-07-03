from flask import Blueprint, render_template

views = Blueprint('views', __name__)#passing the name of the blueprint and the name of the file

@views.route('/')#this is the route for the home page
def home():
    return render_template("home/base.html")
