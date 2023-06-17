from flask import Blueprint,app, render_template
from .models import Player, Tournament, Room
from . import db

host = Blueprint('host', __name__)#passing the name of the blueprint and the name of the file

@host.route('/')#this is the route for the host home page
def home():
    return render_template("host.html")

@host.route('/createTourn')
def createTorun():
    tourn = Tournament(tournamentKey=1)
    db.session.add(tourn)
    db.session.commit()
    return "<h1>TOURNAMENT CREATED</h1>"
