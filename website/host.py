from flask import Blueprint

host = Blueprint('host', __name__)#passing the name of the blueprint and the name of the file

@host.route('/')#this is the route for the host home page
def home():
    return "<h1>HOST</h1>"

