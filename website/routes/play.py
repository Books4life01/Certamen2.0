from flask import Blueprint, render_template, request, redirect, flash, url_for, get_flashed_messages
from ..models import Player, Tournament, Room, Team
from .. import db
from .. import ip

play = Blueprint('play', __name__)#passing the name of the blueprint and the name of the file

@play.route('/')#this is the route for the play home page
def home(): 
    return render_template("home/play.html")


@play.route('/tourn')
def tourn():
    #Get tournKey
    tournPublicKey = request.args.get('tournKey')
    playerPrivateKey = request.args.get('playerKey')
    #retrieve tournament
    tourn = Tournament.getTournByPublic(tournPublicKey)
    player = Player.getPlayerByPrivate(playerPrivateKey)
    if tourn == None:
        flash("Invalid Public Tournament Key")
        return redirect(url_for('play.home'))
    elif player == None:
        flash("Invalid Player Key")
        return redirect(url_for('play.home'))
    else:
        return render_template("client/liveTournClient.html", tournKey=tournPublicKey, player=player.serialize, ipaddress = ip)#also pass in the room and tourn credentials
@play.route('/room')
def room(): 
    #get room key
    roomKey = request.args.get('roomKey')
    playerPrivateKey = request.args.get('playerKey')
    
    room = Room.getRoomByPublic(roomKey)
    player = Player.getPlayerByPrivate(playerPrivateKey)

    if room == None:
        flash("Invalid Public Room Key")
        return redirect(url_for('play.home'))
    elif player == None:
        flash("Invalid Player Key")
        return redirect(url_for('play.home'))
    elif not room.canCompete(player.privateKey):
        flash("Team Occupancy Full")
        return redirect(url_for('play.home'))
    else:
        db.session.commit()
        return render_template("client/liveRoomClient.html", roomKey=roomKey, player=player.serialize, ipaddress = ip)
#______________ INSTANTANEOUS ROUTE__________
@play.route('/joinTourn')
def joinTourn():
    #Get Queries
    publicTournKey = request.args.get('tournKey')
    playerPrivateKey = request.args.get('playerKey')
    playerName = request.args.get('playerName')
    teamKey = request.args.get('teamKey')
    print((publicTournKey, playerPrivateKey, playerName))

    player = Player.getPlayerByPrivate(playerPrivateKey)
    print(player)


    tourn = Tournament.getTournByPublic(publicTournKey)
    
    # if they are attempting to use a playerKey check to see if the player exists and if it doesnt flash error and return a redirect back to the play page
    if playerPrivateKey != '':
        #if the player doesnt exist flash error and return a redirect back to the play page
        if player == None:
            flash("Player Key not found")
            return redirect(url_for('play.home'))
        #otherwise redirect to the tourn page
        else:
            tourn = Tournament.getTournByPrivate(player.superTournament)
            return redirect(url_for('play.tourn', tournKey=tourn.publicKey, playerKey=playerPrivateKey, playerName=playerName, ipaddress = ip))
    else:
        # if tournament doesnt exist flash error and return a redirect back to the play page
        if tourn == None:
            flash("Tournament not found")
            return redirect(url_for('play.home'))
        team = Team.getTeamByPublic(teamKey)
        #if team doesnt exsist at all or in specified tournament flash error and return a redirect back to the play page
        if team == None or team.superTournament != tourn.privateKey:
            flash("Team not found")
            return redirect(url_for('play.home'))
        #other wise create a player and redirect to the tourn page
        playerPrivateKey = tourn.createPlayer(playerName, team.privateKey)
        flash("Your player key is: " + str(playerPrivateKey) + " DO NOT LOSE THIS KEY!")
        return redirect(url_for('play.tourn', tournKey=publicTournKey, playerKey=playerPrivateKey, playerName=playerName, ipaddress = ip))
