from flask import Blueprint, render_template, request, redirect, flash, url_for, get_flashed_messages
from ..models import Player, Tournament, Room
from .. import db

play = Blueprint('play', __name__)#passing the name of the blueprint and the name of the file

@play.route('/')#this is the route for the play home page
def home(): 
    return render_template("home/play.html")


@play.route('/tourn')
def tourn():
    #Get tournKey
    tournPublicKey = request.args.get('tournKey')
    #retrieve tournament
    tourn = Tournament.getTournByPublic(tournPublicKey)
    if tourn == None:
        flash("Invalid Public Tournament Key")
        return redirect(url_for('play.home'))
    else:
        return render_template("client/liveTournClient.html", tournKey=tournPublicKey)#also pass in the room and tourn credentials

#______________ INSTANTANEOUS ROUTE__________
@play.route('/joinTourn')
def joinTourn():
    #Get Queries
    publicTournKey = request.args.get('tournKey')
    playerPrivateKey = request.args.get('playerKey')
    playerName = request.args.get('playerName')
    print((publicTournKey, playerPrivateKey, playerName))

    player = Player.getPlayerByPrivate(playerPrivateKey)

    tourn = Tournament.getTournByPublic(publicTournKey)
    # if tournament doesnt exist flash error and return a redirect back to the play page
    if tourn == None:
        flash("Tournament not found")
        return redirect(url_for('play.home'))
    # if they are attempting to use a playerKey check to see if the player exists and if it doesnt flash error and return a redirect back to the play page
    elif playerPrivateKey != '':
        #if the player doesnt exist flash error and return a redirect back to the play page
        if player == None:
            flash("Player Key not found")
            return redirect(url_for('play.home'))
        #otherwise redirect to the tourn page
        else:
            return redirect(url_for('play.tourn', tournKey=publicTournKey, playerKey=playerPrivateKey, playerName=playerName))
    else:
        playerPrivateKey = tourn.createPlayer(playerName)
        flash("Your player key is: " + str(playerPrivateKey) + " DO NOT LOSE THIS KEY!")
        return redirect(url_for('play.tourn', tournKey=publicTournKey, playerKey=player, playerName=playerName))
