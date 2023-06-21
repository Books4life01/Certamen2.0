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



#________________INSTANTANEOUS ROUTES______

#called from manage.html
@manage.route('/authenticateTourn')
def authenticateToutn():
    tournKey = request.args.get('tournKey')#Retrieve Tournament Key from rewuest

    if Tournament.exists(tournKey):
        return redirect(url_for('host.manage.tourn', tournKey=tournKey))
    else:
        flash("Invalid Tournament Key")
        return redirect(url_for('manage.home'))