from flask import Blueprint,app, render_template, request, flash, redirect, url_for
from ..models import Player, Tournament, Room
from .. import db

host = Blueprint('host', __name__)#passing the name of the blueprint and the name of the file

#______________________HTML ROUTES_____________________

@host.route('/')#this is the route for the host home page
def home():
    return render_template("host.html")
@host.route('/create')
def create():
    return render_template("create.html")


#CREATE SUB ROUTES
@host.route('/create/live')
def createLive():
    #Create new Tournament
    tournKey = Tournament.create(tournName="Certamen Tournament", liveTourn=True)
    return render_template(url_for('host.manage.tourn', tournKey=tournKey))
@host.route('/create/score')
def createScore():
    #do stuff
    return render_template("error.html")


#

  