from flask import Flask, jsonify, request
from flask_socketio import SocketIO

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from os import path
import json

# create database object
db = SQLAlchemy()
#name of the database
DB_NAME = "database.db"
#array which will hold the sockets connected to particular live rooms in format {"roomPrivateKey":{"host":socketId, "clients":[socketId]}}
liveRoomClients = {}

#ip address the server wil be running on so some of the html pages know what socket to onconnect to 
#ip = "http://10.20.2.222:8080"
ip = "http://192.168.4.127:8080"
#172.16.65.246


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

    #registering the blueprints which split the routes into different files
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
    from .routes.updateSocket import on_roomResultUpdate, on_teamAssignmentUpdate, on_liveQuestionUpdate, on_roomCurQuestionNumberOrTypeUpdate
    from .routes.refreshSocket import on_roomDataRefreshRequest, on_tournDataRefreshRequest
    from .routes.baseSocket import on_disconnect, on_roomClientConnect, on_roomHostConnect
    
    #BASES
    # socketio.on_event("connect", on_connect)
    socketio.on_event("disconnect", on_disconnect)
    socketio.on_event("roomClientConnect", on_roomClientConnect)
    socketio.on_event("roomHostConnect", on_roomHostConnect)
    #REFRESHES
    socketio.on_event("roomDataRefreshRequest", on_roomDataRefreshRequest)
    socketio.on_event("tournDataRefreshRequest", on_tournDataRefreshRequest)
    #UPDATES
    socketio.on_event("teamAssignmentUpdate", on_teamAssignmentUpdate)
    socketio.on_event("roomResultUpdate", on_roomResultUpdate)


    socketio.on_event("roomCurQuestionUpdate", on_roomCurQuestionNumberOrTypeUpdate)
    socketio.on_event("liveQuestionUpdate", on_liveQuestionUpdate)
    socketio.on_event("roomCurQuestionTypeUpdate", on_roomCurQuestionNumberOrTypeUpdate)




    return socketio
