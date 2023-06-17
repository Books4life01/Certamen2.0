from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from os import path


db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    #encryotion key
    app.config["key"] = "dskjhfkjdshfkjswwwur"
    #Uniform Resource Identifier link: tells flask where the database is located
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"#format string
    #tell the database the app it is connected to
    db.init_app(app)

    #importing the views file
    from .views import views
    from .play import play
    from .host import host
    from .scorekeep import scorekeep

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(play, url_prefix="/play")
    app.register_blueprint(host, url_prefix="/host", db=db)
    app.register_blueprint(scorekeep, url_prefix="/scorekeep")

    #importing the models from models.py
    from .models import Player, Tournament, Room
    with app.app_context():
        db.create_all()


    
    #create socketio instance
    socketio = SocketIO(app, cors_allowed_origins="*")

    return app
