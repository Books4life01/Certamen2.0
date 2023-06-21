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


#CREATE 'POST' ROUTES
@host.route('/create/live', methods=[ 'POST'])
def createLive():
    #Create new Live Tournament
    tournKey = Tournament.create(tournName=request.form['tournName'], liveTourn=True)
    return redirect(url_for('manage.tourn', tournKey=tournKey))
@host.route('/create/score', methods=[ 'POST'])
def createScore():
    #Create new ScoreBoard Tournament
    tournKey = Tournament.create(tournName=request.form['tournName'], liveTourn=False)
    return redirect(url_for('manage.tourn', tournKey=tournKey))


#

  