from flask import Blueprint, render_template, request, redirect, flash

play = Blueprint('play', __name__)#passing the name of the blueprint and the name of the file

@play.route('/')#this is the route for the play home page
def home(): 
    return render_template("play.html")

@play.route('/joinTourn')
def joinTourn():
    tournCode = request.args.get('tournCode')
    playercode = request.args.get('playercode')
    playerName = request.args.get('playerName')
    
    if True:#if room and tourn credentials are valid
       redirect('/tourn')
    else:
        #if code is invalid
        flash("Invalid Tournament Credentials", category='error')
        # if name is already taken
@play.route('/tourn')
def tourn():
     return render_template("tourn.html", args=request.args)#also pass in the room and tourn credentials
