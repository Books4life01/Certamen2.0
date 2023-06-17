
from . import db#importing from current package the db object

# create Player table/schema, inherits from db.Model
class Player(db.Model):
    playerId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False)
    superTournament = db.Column(db.Integer, db.ForeignKey('tournament.tournamentKey'))

class Tournament(db.Model):
    tournamentKey = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=False)
    players = db.relationship('Player', lazy=True)
    rooms = db.Column(db.Integer, db.ForeignKey('room.roomKey'))
     #Live means the tournament is hosting a virtual game raher than being used as a scoring tool
    liveTourn = db.Column(db.Boolean, unique=False)
class Room(db.Model):
    #key of the room
    roomKey = db.Column(db.Integer, primary_key=True)
    #key of the super Tournament
    superTournament = db.Column(db.Integer, db.ForeignKey('tournament.tournamentKey'))
   
    #Teams in the Room: Max of 4
    teamA = db.Column(db.Integer, db.ForeignKey('team.teamKey'), nullable=True)
    teamB = db.Column(db.Integer, db.ForeignKey('team.teamKey'), nullable=True)
    teamC = db.Column(db.Integer, db.ForeignKey('team.teamKey'), nullable=True)
    teamD = db.Column(db.Integer, db.ForeignKey('team.teamKey'), nullable=True)
class Team(db.Model):
    teamId = db.Column(db.Integer, primary_key=True)
    teamName = db.Column(db.String(100), unique=False)
    #Players in the team: Max of 4
    player1 = db.Column(db.Integer, db.ForeignKey('player.playerId'))
    player2 = db.Column(db.Integer, db.ForeignKey('player.playerId'))
    player3 = db.Column(db.Integer, db.ForeignKey('player.playerId'))
    player4 = db.Column(db.Integer, db.ForeignKey('player.playerId'))
