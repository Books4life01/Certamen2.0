from flask import Blueprint, render_template, request, redirect, flash, url_for
from ..models import Player, Tournament, Room
from .. import db

play = Blueprint('play', __name__)#passing the name of the blueprint and the name of the file

@play.route('/')#this is the route for the play home page
def home(): 
    return render_template("play.html")

@play.route('/joinTourn')
def joinTourn():
    #Get Queries
    tournKey = request.args.get('tournKey')
    playerKey = request.args.get('playerKey')
    playerName = request.args.get('playerName')

    # if tournament doesnt exist flash error and return a redirect back to the play page
    if not Tournament.exists(tournKey):
        flash("Tournament not found")
        return redirect("/play")
    # if they are attempting to use a playerKey check to see if the player exists and if it doesnt flash error and return a redirect back to the play page
    elif playerKey != None and not Player.exists(playerKey):
        flash("Player Key not found")
        return redirect(url_for('play.home'))
    #otherwise redirect to the tourn page
    else:
      return redirect(url_for('play.tourn', tournKey=tournKey, playerKey=playerKey, playerName=playerName))
@play.route('/tourn')
def tourn():
     return render_template("tourn.html", args=request.args)#also pass in the room and tourn credentials
