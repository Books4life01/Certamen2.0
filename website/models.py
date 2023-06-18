
from . import db#importing from current package the db object
import random

# create Player table/schema, inherits from db.Model
class Player(db.Model):
    playerId = db.Column(db.Integer, primary_key=True, unique=True)
    playerKey = db.Column(db.String(8), unique=True)
    name = db.Column(db.String(100), unique=False)
    superTournament = db.Column(db.Integer, db.ForeignKey('tournament.tournamentKey'))

    #FUNCTIONS
    #see if a player exsists
    @staticmethod
    def exists(playerCode):
        player = db.session.query(Player).filter_by(playerCode=playerCode).first()
        if player:
            return True
        else:
            return False

class Tournament(db.Model):
    #id is used to identify the tournament
    tournamentId = db.Column(db.Integer, unique=True,primary_key=True)
    #key is used to manage the tournament
    tournamentKey = db.Column(db.String(8), unique=True)
    #name of the tournament
    name = db.Column(db.String(200), unique=False)
    #players in the tournament
    players = db.relationship('Player', lazy=True)
    #rooms in the tournament
    rooms = db.Column(db.Integer, db.ForeignKey('room.roomKey'))
     #Live means the tournament is hosting a virtual game raher than being used as a scoring tool
    liveTourn = db.Column(db.Boolean, unique=False)

    #FUNCTIONS
    #see if a tournament exsists
    @staticmethod
    def exists(tournKey):
        tourn = db.session.query(Tournament).filter_by(tournamentKey=tournKey).first()
        if tourn:
            return True
        else:
            return False
    #create a new tournament passing its name and if it is live or not
    @staticmethod
    def create(tournName, liveTourn):
        #Generate a Key
        key = Tournament.generateKey()
        #Create a new tournament passing the key, name, and if it is live or not; id is auto generated
        tourn = Tournament(name=tournName, liveTourn=liveTourn, tournamentKey=key)
        db.session.add(tourn)
        db.session.commit()
        return key
    @staticmethod
    def generateKey():
        key = ""
        values = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        #Create a key while the key is empty or the key already exists
        while len(key) ==0 or Tournament.exists(key):
            key = "" #reset key
            #create a key of 8 characters using lower and upper case letters and numbers
            #62^8=218,340,105,584,896 possible keys a lot
            while len(key) < 8:
                key += values[random.randint(0, len(values) - 1)]
        return key
        
class Room(db.Model):
     #id of the room
    roomId = db.Column(db.Integer, unique=True,primary_key=True)
    #key of the room
    roomKey = db.Column(db.String(8), unique=True)
    #key of the super Tournament
    superTournament = db.Column(db.Integer, db.ForeignKey('tournament.tournamentId'))
   
    #Teams in the Room: Max of 4
    teamA = db.Column(db.Integer, db.ForeignKey('team.teamId'), nullable=True)
    teamB = db.Column(db.Integer, db.ForeignKey('team.teamId'), nullable=True)
    teamC = db.Column(db.Integer, db.ForeignKey('team.teamId'), nullable=True)
    teamD = db.Column(db.Integer, db.ForeignKey('team.teamId'), nullable=True)
class Team(db.Model):
    #id of the team
    teamId = db.Column(db.Integer, primary_key=True, unique=True)
    #used to join a team
    teamKey = db.Column(db.String(8), unique=True)
    #name of the team
    teamName = db.Column(db.String(100), unique=False)
    #Players in the team: Max of 4
    player1 = db.Column(db.Integer, db.ForeignKey('player.playerId'))
    player2 = db.Column(db.Integer, db.ForeignKey('player.playerId'))
    player3 = db.Column(db.Integer, db.ForeignKey('player.playerId'))
    player4 = db.Column(db.Integer, db.ForeignKey('player.playerId'))
