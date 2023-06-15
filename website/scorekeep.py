from flask import Blueprint

scorekeep = Blueprint('scorekeep', __name__)#passing the name of the blueprint and the name of the file

@scorekeep.route('/')#this is the route for the play home page
def home(): 
    return "<h1>SCOREKEEP</h1>"
