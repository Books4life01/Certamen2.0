
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
    #create a new player
    @staticmethod
    def createPlayer(playerName, tournamentKey):
        key = Player.generatePlayerKey()
        player = Player(name=playerName, superTournament=tournamentKey, playerKey=key)
        return player
    #generate a key for the player
    @staticmethod
    def generateKey():
        key = ""
        values = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        #Create a key while the key is empty or the key already exists
        while len(key) ==0 or Player.exists(key):
            key = "" #reset key
            #create a key of 8 characters using lower and upper case letters and numbers
            #62^8=218,340,105,584,896 possible keys a lot
            while len(key) < 8:
                key += values[random.randint(0, len(values) - 1)]
        return key
    

class Tournament(db.Model):
    #id is used to identify the tournament
    tournamentId = db.Column(db.Integer, unique=True,primary_key=True)
    #key is used to manage the tournament
    tournamentKey = db.Column(db.String(8), unique=True)
    #name of the tournament
    name = db.Column(db.String(200), unique=False)
    #players in the tournament
    players = db.relationship('Player', lazy=True, backref='tournament', cascade="all, delete-orphan")#cascade deletes all objects when tournament is deleted; orphan only deletes if objecct doesnt belong to another tournament
       #rooms in the tournament
    rooms = db.relationship('Room', lazy=True, backref='tournament', cascade="all, delete-orphan")
    #teams in the tournament
    teams = db.relationship('Team', lazy=True, backref='tournament', cascade="all, delete-orphan")
    #Live means the tournament is hosting a virtual game raher than being used as a scoring tool
    liveTourn = db.Column(db.Boolean, unique=False)

    #FUNCTIONS
    #create new room for the tournament
    def createRoom(self, roomName):
        room = Room.createRoom(roomName, self.tournamentKey)
        self.rooms.append(room)
        db.session.commit()#commiting because we are changing the database
        return room.roomKey
    #add a team to the tournament
    def createTeam(self, teamName):
        team = Team.createTeam(teamName, self.tournamentKey)
        self.teams.append(team)
        db.session.commit()
        return team.teamKey
    #add a player to the tournament
    def createPlayer(self, playerName):
        player = Player.createPlayer(playerName, self.tournamentKey)
        self.players.append(player)
        db.session.commit()
        return player.playerKey
    #get a tournaments list of teams
    def getTeams(self):
        return [team.serialize for team in self.teams]
    #get a tournaments list of rooms
    def getRooms(self):
        return [room.serialize for room in self.rooms]
    #get a tournaments list of players
    def getPlayers(self):
        return [player.serialize for player in self.players]
    
    #delete a tournament
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    
    #__________STATIC_____________
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
    #generate a key for the tournament
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
    superTournamentKey = db.Column(db.String(8), db.ForeignKey('tournament.tournamentKey'))
    #name of the room
    roomName = db.Column(db.String(200), unique=False)

    #Questions Results in the room
    results = db.relationship('Result', lazy=True, backref='room')

    #active Question Number
    currentQuestion = db.Column(db.Integer, unique=False, default=1)    

    



   
    #Teams in the Room: Max of 4
    teamA = db.Column(db.Integer, db.ForeignKey('team.teamId'), nullable=True)
    teamB = db.Column(db.Integer, db.ForeignKey('team.teamId'), nullable=True)
    teamC = db.Column(db.Integer, db.ForeignKey('team.teamId'), nullable=True)
    teamD = db.Column(db.Integer, db.ForeignKey('team.teamId'), nullable=True)

    #return the selectedTeams in the room
    def getTeams(self):
        return {"teams":(self.teamA, self.teamB, self.teamC, self.teamD)}
    #get Results in the room
    def getResults(self):
        return [result.serialize for result in self.results]
    def addResult(self, teamLetter, playerNumber, questionNumber, tossupAchieved, bonus1Achieved, bonus2Achieved):
        result = Result(teamLetter=teamLetter, playerNumber=playerNumber, questionNumber=questionNumber, tossup=tossupAchieved, bonus1=bonus1Achieved, bonus2=bonus2Achieved)
        db.session.add(result)
        self.results.append(result)
        db.session.commit()

    #@property is used to make a function act like a variable
    @property
    def isLive(self):
        return db.query(Tournament).filter_by(tournamentKey=self.superTournamentKey).first().liveTourn
    #serialize the room object by converting it to a dictionary; we do this so we can send it as a json object
    @property
    def serialize(self):
        return {
            'roomId': self.roomId,
            'roomKey': self.roomKey,
            'superTournament': self.superTournamentKey,
            'roomName': self.roomName,
            'teamA': self.teamA,
            'teamB': self.teamB,
            'teamC': self.teamC,
            'teamD': self.teamD
        }
    #STATIC FUNCTIONS
    #see if a room exsists
    @staticmethod
    def exists(roomKey):
        room = db.session.query(Room).filter_by(roomKey=roomKey).first()
        if room:
            return True
        else:
            return False
    @staticmethod
    def createRoom(roomName, superTournamentKey):
        #Generate a Key
        key = Room.generateRoomKey()
        #Create a new room passing the key, name, and if it is live or not; id is auto generated
        room = Room(roomName=roomName, superTournamentKey=superTournamentKey, roomKey=key)
        db.session.add(room)
        db.session.commit()
        return room
    #generates a unique key for the room
    @staticmethod
    def generateRoomKey():
        key = ""
        values = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        #Create a key while the key is empty or the key already exists
        while len(key) ==0 or Room.exists(key):
            key = "" #reset key
            #create a key of 8 characters using lower and upper case letters and numbers
            #62^8=218,340,105,584,896 possible keys a lot
            while len(key) < 8:
                key += values[random.randint(0, len(values) - 1)]
        return key
    


class Team(db.Model):
    #id of the team
    teamId = db.Column(db.Integer, primary_key=True, unique=True)
    #used to join a team
    teamKey = db.Column(db.String(8), unique=True)
    #name of the team
    teamName = db.Column(db.String(100), unique=False)
    #key of the super tournament
    superTournamentKey = db.Column(db.String(8), db.ForeignKey('tournament.tournamentKey'))

    #Players in the team: Max of 4
    player1 = db.Column(db.Integer, db.ForeignKey('player.playerId'))
    player2 = db.Column(db.Integer, db.ForeignKey('player.playerId'))
    player3 = db.Column(db.Integer, db.ForeignKey('player.playerId'))
    player4 = db.Column(db.Integer, db.ForeignKey('player.playerId'))

    #FUNCTIONS
    #serialize the team object by converting it to a dictionary; we do this so we can send it as a json object
    @property
    def serialize(self):
        return {
            'teamId': self.teamId,
            'teamKey': self.teamKey,
            'teamName': self.teamName,
            'superTournament': self.superTournamentKey,
            'player1': self.player1,
            'player2': self.player2,
            'player3': self.player3,
            'player4': self.player4
        }

    #STATIC FUNCTIONS
    #see if a team exsists
    @staticmethod
    def exists(teamKey):
        team = db.session.query(Team).filter_by(teamKey=teamKey).first()
        if team:
            return True
        else:
            return False
    #create a new team
    @staticmethod
    def createTeam(teamName, superTournamentKey):
        #Generate a Key
        key = Team.generateTeamKey()
        #Create a new team passing the key, name, and if it is live or not; id is auto generated
        team = Team(teamName=teamName, superTournamentKey=superTournamentKey, teamKey=key)
        db.session.add(team)
        db.session.commit()
        return team
    #generates a unique key for the team
    @staticmethod
    def generateTeamKey():
        key = ""
        values = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        #Create a key while the key is empty or the key already exists
        while len(key) ==0 or Room.exists(key):
            key = "" #reset key
            #create a key of 8 characters using lower and upper case letters and numbers
            #62^8=218,340,105,584,896 possible keys a lot
            while len(key) < 8:
                key += values[random.randint(0, len(values) - 1)]
        return key
    
class Result(db.Model):
    #id of the result
    resultId = db.Column(db.Integer, primary_key=True, unique=True)
    #team that got the question right: Team ABCorD
    teamLetter = db.Column(db.String(1), unique=False)
    #player that got the question right: Player 1, 2, 3, or 4
    playerNumber = db.Column(db.String(1), unique=False)
    #room that the question was in
    roomKey = db.Column(db.Integer, db.ForeignKey('room.roomKey'))

    #QuestionNumber
    questionNumber = db.Column(db.Integer, unique=False)
    
    #tossup achieved?
    tossup = db.Column(db.Boolean, unique=False)
    #bonuses achieved?
    bonus1 = db.Column(db.Boolean, unique=False)
    bonus2 = db.Column(db.Boolean, unique=False)

    #calculate the total points
    @property
    def totalPoints(self):
        return 10 if self.tossup else 0 + 5 if self.bonus1 else 0 + 5 if self.bonus2 else 0
    #serialize the result object by converting it to a dictionary; we do this so we can send it as a json object
    @property
    def serialize(self):
        return {
            'resultId': self.resultId,
            'questionNumber': self.questionNumber,
            'teamLetter': self.teamLetter,
            'playerNumber': self.playerNumber,
            'roomKey': self.roomKey,
            'tossup': self.tossup,
            'bonus1': self.bonus1,
            'bonus2': self.bonus2,
            'totalPoints': self.totalPoints
        }


    