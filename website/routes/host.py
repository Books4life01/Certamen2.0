from flask import Blueprint,app, render_template, request, flash, redirect, url_for
from ..models import Player, Tournament, Room
from .. import db

host = Blueprint('host', __name__)#passing the name of the blueprint and the name of the file

#______________________HTML ROUTES_____________________

@host.route('/')#this is the route for the host home page
def home():
    return render_template("home/host.html")
@host.route('/create')#this is the route for the host create page
def create():
    return render_template("home/create.html")


#CREATE 'POST' ROUTES
@host.route('/create/live', methods=[ 'POST'])
def createLive():
    #Create new Live Tournament and redirect to the tournament page
    tourn = Tournament.create(name=request.form['name'], liveTourn=True)
    return redirect(url_for('manage.tourn', tournKey=tourn.privateKey))
@host.route('/create/score', methods=[ 'POST'])
def createScore():
    #Create new ScoreBoard Tournament
    tourn = Tournament.create(name=request.form['name'], liveTourn=False)
    return redirect(url_for('manage.tourn', tournKey=tourn.privateKey))


#

  