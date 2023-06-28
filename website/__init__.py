from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from os import path
import json


db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    #encryotion key
    app.config["SECRET_KEY"] = "dskjhfkjdshfkjswwwur"
    #Uniform Resource Identifier link: tells flask where the database is located
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"#format string
    #tell the database the app it is connected to
    db.init_app(app)

    #importing the views file
    from .views import views
    from .routes.play import play
    from .routes.host import host
    from .routes.manage import manage

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(play, url_prefix="/play", db=db)
    app.register_blueprint(host, url_prefix="/host", db=db)
    app.register_blueprint(manage, url_prefix="/host/manage", db=db)

    #importing the models from models.py
    from .models import Player, Tournament, Room, Team, Result
    #create the database
    with app.app_context():
        db.create_all()


    
   


    return app

#set up socket server
def createSocketServer(app):
    #create socket server
    socketio = SocketIO(app, cors_allowed_origins="*")

    #import models
    from .models import Player, Tournament, Room, Team, Result
    
    #Manage Connection
    @socketio.on('connect')
    def connect():
        print("Connected")
    

    #On data Refresh Request
    @socketio.on('tournDataRefreshRequest')
    def refresh(message):
        #retrieve request data
        tournKey = message["tournKey"]

        print("Tourn Data Refresh Requested")
        #Grab tournnament object from database using tournKey
        tourn = Tournament.query.filter_by(tournamentKey=tournKey).first()

        #retrieve list of rooms(list of objects) from tournament object
        rooms = tourn.getRooms()
        #send room data to client
        socketio.emit('roomsUpdate', rooms)
        print("Rooms Data Sent")

        #retrieve list of teams(list of objects) from tournament object
        teams = tourn.getTeams()
        socketio.emit('teamsUpdate', teams)
    @socketio.on('roomDataRefreshRequest')
    def refresh(message):
        print(message)
        #retrieve roomKey from request
        roomKey = message["roomKey"]
        
        #grab  the superTournKey from the room database 
        superTournKey = Room.query.filter_by(roomKey=roomKey).first().superTournamentKey
        #grab the tournament object from the database using the superTournKey
        tourn = Tournament.query.filter_by(tournamentKey=superTournKey).first()
        #retrieve list of teams(list of objects) from tournament object
        teams = tourn.getTeams()
        #send data to client
        socketio.emit('tournTeamsUpdate', teams)

        room = Room.query.filter_by(roomKey=roomKey).first()
        roomTeams = room.getTeams()
        socketio.emit('roomTeamsUpdate', roomTeams)

        results = room.getResults()
        outResults = {
            "curQuestion": room.currentQuestion,
            "resultList": results,
        }
        socketio.emit('roomResultsUpdate', outResults)

    

    @socketio.on('teamAssignmentUpdate')
    def refresh(message):
        #retrieve request data
        roomKey = message["roomKey"]
        teamA,teamB,teamC,teamD = message["teamA"],message["teamB"],message["teamC"],message["teamD"]

        room = Room.query.filter_by(roomKey=roomKey).first()
        room.teamA = teamA
        room.teamB = teamB
        room.teamC = teamC
        room.teamD = teamD
        db.session.commit()
        print("Team Assignment Updated")

        #TO-DO: send Updated team assignment to any clients connected to the room
    
    @socketio.on('roomResultUpdate')
    def refresh(message):
        #retrieve request data
        roomKey = message["roomKey"]
        tossup, bonus1, bonus2 = message["tossup"],message["bonus1"],message["bonus2"]
        teamLetter,playerNum = message["teamLetter"],message["teamMember"]
        questionNum = message["questionNum"]
        roomCurQuestion = message["roomCurQuestion"]

        #retrieve room
        room = Room.query.filter_by(roomKey=roomKey).first()
        #update current question
        room.currentQuestion = roomCurQuestion


        #retrieve Results list from room
        results = room.results
        
        #if the result doesnt exsist yet create it 
        if(len(results) < questionNum):
            room.addResult(teamLetter,playerNum,questionNum, tossup, bonus1, bonus2)
        else:
            #otherwise update the result
            room.results[questionNum-1].tossup = tossup
            room.results[questionNum-1].bonus1 = bonus1
            room.results[questionNum-1].bonus2 = bonus2
            room.results[questionNum-1].teamLetter = teamLetter
            room.results[questionNum-1].playerNumber = playerNum
            room.results[questionNum-1].questionNum = questionNum
        db.session.commit()

            






    return socketio
