from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
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
    from .models import Player, Tournament, Room, Team
    #create the database
    with app.app_context():
        db.create_all()


    
   


    return app
def createSocketServer(app):
    socketio = SocketIO(app, cors_allowed_origins="*")

    #import models
    from .models import Player, Tournament, Room, Team
    
    #Manage Connection
    @socketio.on('connect')
    def connect():
        print("Connected")
    

    #On data Refresh Request
    @socketio.on('tournDataRefreshRequest')
    def refresh(message):
        #retrieve request data
        tournKey = message["tournKey"]

        print("Data Refresh Requested")
        #Grab room Data from database
        rooms = Room.query.filter_by(superTournamentKey=tournKey).all()
        #convert to list of dicts
        rooms = [room.serialize for room in rooms]
       

        socketio.emit('roomsUpdate', rooms)

    return socketio
