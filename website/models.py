from . import db#importing from current package the db object

# create Player table/schema, inherits from db.Model
class Player(db.Model):
    playerId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False)
    superTournament = db.Column(db.Integer, db.ForeignKey('tournament.tournamentKey'))

class Tournament(db.Model):
    tournamentKey = db.Column(db.Integer, primary_key=True)
    players = db.relationship('Player', lazy=True)
    rooms = db.Column(db.Integer, db.ForeignKey('room.roomKey'))
class Room(db.Model):
    roomKey = db.Column(db.Integer, primary_key=True)
    superTournament = db.Column(db.Integer, db.ForeignKey('tournament.tournamentKey'))

