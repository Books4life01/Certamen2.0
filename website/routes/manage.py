from flask import Blueprint, render_template, request, redirect, flash, url_for
from ..models import Player, Tournament, Room
from .. import db

manage = Blueprint('manage', __name__)#passing the name of the blueprint and the name of the file

@manage.route('/')#this is the route for the host home page
def home():
        return render_template("home/manage.html")
@manage.route('/tourn')
def tourn():
     #retrieve tourn private key from request
     tournPrivateKey = request.args.get('tournKey')
     tourn = Tournament.getTournByPrivate(tournPrivateKey) 
     if tourn == None:
            flash("Invalid Private Tournament Key")
            return redirect(url_for('manage.home'))
     else:
        #retrieve object and check if it is a live tournament
        isLive = tourn.liveTourn
        if isLive:
            return render_template("host/liveTournHost.html", tournKey=tournPrivateKey)
        else:
            return render_template("host/scoreTournHost.html", tournKey=tournPrivateKey)
@manage.route('/room')
def room():
        roomPrivateKey = request.args.get('roomKey')
        room = Room.getRoomByPrivate(roomPrivateKey)
        if room == None:
            flash("Invalid Private Room Key")
            return redirect(url_for('manage.home'))
        else:
            if room.isLiveRoom:
                return render_template("host/liveRoomHost.html", roomKey=roomPrivateKey)
            else:
                return render_template("host/scoreRoomHost.html", roomKey=roomPrivateKey)

     

#post routes
@manage.route('/tourn/room', methods=['POST'])
def createRoom():
    #get the tournament key from the request
    tournPrivateKey = request.form['tournKey']
    #get the room name from the request
    roomName = request.form['roomName']
    #creates a room and returns the room key
    tourn = Tournament.getTournByPrivate(tournPrivateKey)
    tourn.createRoom(roomName)
    return redirect(url_for('manage.tourn', tournKey=tournPrivateKey))
@manage.route('/tourn/team', methods=['POST'])
def createTeam():
    #get the tournament key from the request
    tournPrivateKey = request.form['tournKey']
    #get the team name from the request
    name = request.form['teamName']
    #creates a team and returns the team key
    tourn = Tournament.getTournByPrivate(tournPrivateKey)
    tourn.createTeam(name)
    return redirect(url_for('manage.tourn', tournKey=tournPrivateKey))
#delete routes
@manage.route('/tourn', methods=['DELETE'])
def deleteTourn():
    tournPrivateKey = request.args.get('tournKey')
    tourn = Tournament.getTournByPrivate(tournPrivateKey)
    tourn.delete()
    return ""
@manage.route('/room', methods=['DELETE'])
def deleteRoom():
    roomPrivateKey = request.args.get('roomKey')
    room = Room.getRoomByPrivate(roomPrivateKey)
    room.delete()
    return ""

    
     


#________________INSTANTANEOUS ROUTES______

#called from manage.html
@manage.route('/authenticateTourn')
def authenticateToutn():
    tournPrivateKey = request.args.get('tournKey')#Retrieve Tournament Key from request

    if Tournament.getTournByPrivate(tournPrivateKey):
        return redirect(url_for('manage.tourn', tournKey=tournPrivateKey))
    else:
        flash("Invalid Tournament Key")
        return redirect(url_for('manage.home'))