from flask import Blueprint, render_template, request, redirect, flash, url_for
from ..models import Player, Tournament, Room
from .. import db

manage = Blueprint('manage', __name__)#passing the name of the blueprint and the name of the file

@manage.route('/')#this is the route for the host home page
def home():
        return render_template("manage.html")
@manage.route('/tourn')
def tourn():
     tournKey = request.args.get('tournKey')
     isLive = db.session.query(Tournament).filter_by(tournamentKey=tournKey).first().liveTourn
     if isLive:
          return render_template("liveTourn.html", tournKey=tournKey)
     else:
            return render_template("scoreBoardTourn.html", tournKey=tournKey)
@manage.route('/room')
def room():
        roomKey = request.args.get('roomKey')
        return render_template("scoreRoom.html", roomKey=roomKey)

     

#post routes
@manage.route('/tourn/room', methods=['POST'])
def createRoom():
    #get the tournament key from the request
    tournKey = request.form['tournKey']
    #get the room name from the request
    roomName = request.form['roomName']
    #creates a room and returns the room key
    tourn = db.session.query(Tournament).filter_by(tournamentKey=tournKey).first()
    roomKey = tourn.createRoom(roomName)
    return redirect(url_for('manage.tourn', tournKey=tournKey))
@manage.route('/tourn/team', methods=['POST'])
def createTeam():
    #get the tournament key from the request
    tournKey = request.form['tournKey']
    #get the team name from the request
    teamName = request.form['teamName']
    #creates a team and returns the team key
    tourn = db.session.query(Tournament).filter_by(tournamentKey=tournKey).first()
    teamKey = tourn.createTeam(teamName)
    return redirect(url_for('manage.tourn', tournKey=tournKey))
    
     


#________________INSTANTANEOUS ROUTES______

#called from manage.html
@manage.route('/authenticateTourn')
def authenticateToutn():
    tournKey = request.args.get('tournKey')#Retrieve Tournament Key from rewuest

    if Tournament.exists(tournKey):
        return redirect(url_for('manage.tourn', tournKey=tournKey))
    else:
        flash("Invalid Tournament Key")
        return redirect(url_for('manage.home'))