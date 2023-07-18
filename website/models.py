
from . import db#importing from current package the db object
import random

# create Player table/schema, inherits from db.Model
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    publicKey = db.Column(db.String(8), unique=True)
    privateKey = db.Column(db.String(8), unique=True)
    name = db.Column(db.String(100), unique=False)
    superTournament = db.Column(db.Integer, db.ForeignKey('tournament.privateKey'))
    superTeam = db.Column(db.Integer, db.ForeignKey('team.privateKey'))



    #FUNCTIONS
    @property
    def serialize(self):
        return {
            'publicKey': self.publicKey,
            'privateKey': self.privateKey,
            'name': self.name,
            'superTournament': self.superTournament,
            'superTeam': self.superTeam
        }

    #see if a player exsists by its key either public or private
    @staticmethod
    def exists(publicKey):
        public = db.session.query(Player).filter_by(publicKey=publicKey).first()
        private = db.session.query(Player).filter_by(privateKey=publicKey).first()
        return private != None or public != None
    #create a new player
    @staticmethod
    def createPlayer(playerName, tournamentKey, teamKey):
        privateKey = Player.generateKey()
        publicKey = Player.generateKey(privateKey)
        player = Player(name=playerName, superTournament=tournamentKey, superTeam = teamKey, publicKey=publicKey, privateKey=privateKey)
        return player
    #generate a key for the player ensuring it is unique and not the same as the provided invalid key argumeny
    @staticmethod
    def generateKey(invalidKey = None):
        key = ""
        values = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        #Create a key while the key is empty or the key already exists
        while len(key) ==0 or Player.exists(key) or key == invalidKey:
            key = "" #reset key
            #create a key of 8 characters using lower and upper case letters and numbers
            #62^8=218,340,105,584,896 possible keys a lot
            while len(key) < 8:
                key += values[random.randint(0, len(values) - 1)]
        return key
    @staticmethod
    def getPlayerByPublic(publicKey):
        return db.session.query(Player).filter_by(publicKey=publicKey).first()
    @staticmethod
    def getPlayerByPrivate(privateKey):
        return db.session.query(Player).filter_by(privateKey=privateKey).first()

    

class Tournament(db.Model):
    #id is used to identify the tournament
    id = db.Column(db.Integer, unique=True,primary_key=True)
    #private key is used to manage the tournament as an admin/host
    privateKey = db.Column(db.String(8), unique=True)
    #public key is used to access the tournament as a player
    publicKey = db.Column(db.String(8), unique=True)
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
    #create new room for the tournament return the room's private key
    def createRoom(self, roomName):
        room = Room.createRoom(roomName, self.privateKey)
        self.rooms.append(room)
        db.session.commit()#commiting because we are changing the database
        return room.privateKey
    #add a team to the tournament return the team's private key
    def createTeam(self, teamName):
        team = Team.createTeam(teamName, self.privateKey)
        self.teams.append(team)
        db.session.commit()
        return team.privateKey
    #add a player to the tournament reutrn the player's private key
    def createPlayer(self, playerName, teamKey):
        player = Player.createPlayer(playerName, self.privateKey, teamKey)
        self.players.append(player)
        db.session.commit()
        return player.privateKey
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
    @property
    def serialize(self):
        return {
            'privateKey': self.privateKey,
            'publicKey': self.publicKey,
            'name': self.name,
            'players': self.getPlayers(),
            'rooms': self.getRooms(),
            'teams': self.getTeams(),
            'liveTourn': self.liveTourn
        }

    
    
    #__________STATIC_____________
   
    #sees if a tournament exsists by its key either public or private
    @staticmethod
    def exists(key):
        public = db.session.query(Tournament).filter_by(publicKey=key).first()
        private = db.session.query(Tournament).filter_by(privateKey=key).first()
        return private != None or public != None
    #create a new tournament passing its name and if it is live or not
    @staticmethod
    def create(name, liveTourn):
        #Generate a Key
        private = Tournament.generateKey()
        public = Tournament.generateKey(private)
        #Create a new tournament passing the key, name, and if it is live or not; id is auto generated
        tourn = Tournament(name=name, liveTourn=liveTourn, privateKey=private, publicKey=public)
        db.session.add(tourn)
        db.session.commit()
        return tourn
    #generate a key for the tournament
    @staticmethod
    def generateKey(invalidKey = None):
        key = ""
        values = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        #Create a key while the key is empty or the key already exists
        while len(key) ==0 or Tournament.exists(key) or key == invalidKey:
            key = "" #reset key
            #create a key of 8 characters using lower and upper case letters and numbers
            #62^8=218,340,105,584,896 possible keys a lot
            while len(key) < 8:
                key += values[random.randint(0, len(values) - 1)]
        return key
    @staticmethod
    def getTournByPrivate(privateKey):
        return db.session.query(Tournament).filter_by(privateKey=privateKey).first()
    @staticmethod
    def getTournByPublic(publicKey):
        return db.session.query(Tournament).filter_by(publicKey=publicKey).first()
    @staticmethod
    def getTourn(key):
        return Tournament.getTournByPrivate(key) or Tournament.getTournByPublic(key)

    

    
        
class Room(db.Model):
     #id of the room
    id = db.Column(db.Integer, unique=True,primary_key=True)
    #key of the room
    publicKey = db.Column(db.String(8), unique=True)
    #publicKey of the room
    privateKey = db.Column(db.String(8), unique=True)
    #key of the super Tournament
    superTournament = db.Column(db.String(8), db.ForeignKey('tournament.privateKey'))
    #name of the room
    name = db.Column(db.String(200), unique=False)

    #Questions Results in the room
    results = db.relationship('Result', lazy=True, backref='room')

    #active Question Number
    currentQuestion = db.Column(db.Integer, unique=False, default=1)  
    #active Question Type: so if tossup is being asked, or bonus1, or bonus2
    curQuestionType = db.Column(db.Integer, unique=False, default=0)#0=Tossup, 1=Bonus1, 2=Bonus2
    #current Live Question: the question that is currently being asked
    curLiveQuestion = db.Column(db.String(2000),  nullable=True, default="")
    #current Live Question Answer: the attempted answer to the question that is currently being asked
    curLiveQuestionAnswer = db.Column(db.String(2000),  nullable=True, default="")
    #teamsAttempted: teams that have attempted to answer the question and failed
    playersAttempted = db.Column(db.String(2000), unique=False, default=0)
    #whether or not the question is paused for answer inspection
    liveQuestionPaused = db.Column(db.Boolean, unique=False, default=False)
    #isLive determines if the room is live or not: it is live if a client is currently managing the room
    isLive = db.Column(db.Boolean, unique=False)



   
    #Teams in the Room: Max of 4
    teamA = db.Column(db.Integer, db.ForeignKey('team.privateKey'), nullable=True)
    teamB = db.Column(db.Integer, db.ForeignKey('team.privateKey'), nullable=True)
    teamC = db.Column(db.Integer, db.ForeignKey('team.privateKey'), nullable=True)
    teamD = db.Column(db.Integer, db.ForeignKey('team.privateKey'), nullable=True)
    #players currently live from each team
    teamAPlayers = db.Column(db.Integer, unique=False, default=0)
    teamBPlayers = db.Column(db.Integer, unique=False, default=0)
    teamCPlayers = db.Column(db.Integer, unique=False, default=0)
    teamDPlayers = db.Column(db.Integer, unique=False, default=0)

    #return the selectedTeams in the room
    def getTeams(self):
        return [self.teamA, self.teamB, self.teamC, self.teamD]
    #get Results in the room
    def getResults(self):
        return [result.serialize for result in self.results]
    def addResult(self, teamLetter, playerNumber, questionNumber, tossupAchieved, bonus1Achieved, bonus2Achieved, tossupQuestion="None", bonus1Question="None", bonus2Question="None"):
        result = Result(teamLetter=teamLetter, playerNumber=playerNumber, questionNumber=questionNumber, tossup=tossupAchieved, bonus1=bonus1Achieved, bonus2=bonus2Achieved, tossupQuestion=tossupQuestion, bonus1Question=bonus1Question, bonus2Question=bonus2Question, superRoom = self.publicKey)
        db.session.add(result)
        self.results.append(result)
        db.session.commit()
    def canCompete(self, playerKey):
        #retrieve player superTeam
        player = Player.getPlayer(playerKey)
        if player == None: return False
        superTeam = player.superTeam
        #ensure room isLive
        if not self.isLive: return False
        #check if the player's superTeam is in the room
        return superTeam == self.teamA and self.teamAPlayers < 4 or superTeam == self.teamB and self.teamBPlayers < 4 or superTeam == self.teamC and self.teamCPlayers < 4 or superTeam == self.teamD and self.teamDPlayers < 4
   #adds a player to the room given a teamKey and increments the number of players in the team
    def addLivePlayer(self, playerKey):
        if self.canCompete(playerKey):
            player = Player.getPlayer(playerKey)
            superTeam = player.superTeam
            if superTeam == self.teamA:
                self.teamAPlayers += 1
            elif superTeam == self.teamB:
                self.teamBPlayers += 1
            elif superTeam == self.teamC:
                self.teamCPlayers += 1
            elif superTeam == self.teamD:
                self.teamDPlayers += 1
            db.session.commit()
            return True
        return False
    #removes a player from the room given a teamKey and decrements the number of players in the team
    #eamKey is the private key of the team
    def removeLivePlayer(self, teamKey):
        if teamKey == self.teamA and self.teamAPlayers > 0:
            self.teamAPlayers -= 1
        elif teamKey == self.teamB and self.teamBPlayers > 0:
            self.teamBPlayers -= 1
        elif teamKey == self.teamC and self.teamCPlayers > 0:
            self.teamCPlayers -= 1
        elif teamKey == self.teamD and self.teamDPlayers > 0:
            self.teamDPlayers -= 1
        db.session.commit()
    def addAttemptedPlayer(self, playerKey):
        player = Player.getPlayer(playerKey)
        if player == None: return False
        self.playersAttempted += player.name + ", "
        db.session.commit()
        return True
    def clearAttemptedPlayers(self):
        self.playersAttempted = ""
        db.session.commit()
    def getAttemptedPlayers(self):
        return self.playersAttempted.split(", ")
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
    #@property is used to make a function act like a variable
    @property
    def isLiveRoom(self):
        return Tournament.getTournByPrivate(self.superTournament).liveTourn
    #serialize the room object by converting it to a dictionary; we do this so we can send it as a json object
    @property
    def serialize(self):
        return {
            'id': self.id,
            'privateKey': self.privateKey,
            'publicKey': self.publicKey,
            'superTournament': self.superTournament,
            'name': self.name,
            'isLive': self.isLive,
            'teamA': self.teamA,
            'teamB': self.teamB,
            'teamC': self.teamC,
            'teamD': self.teamD,
            'teamAPlayers': self.teamAPlayers,
            'teamBPlayers': self.teamBPlayers,
            'teamCPlayers': self.teamCPlayers,
            'teamDPlayers': self.teamDPlayers,
            'curQuestionType': self.curQuestionType,
            'currentQuestion': self.currentQuestion,
            'curLiveQuestion': self.curLiveQuestion,
            'curLiveQuestionAnswer': self.curLiveQuestionAnswer,
            'liveQuestionPaused': self.liveQuestionPaused,
            'playersAttempted': self.getAttemptedPlayers()
        }
    #STATIC FUNCTIONS
    #see if a room exsists with either a piblic or private key
    @staticmethod
    def exists(key):
        publicRoom = db.session.query(Room).filter_by(publicKey=key).first()
        privateRoom = db.session.query(Room).filter_by(privateKey=key).first()
        return publicRoom != None or privateRoom != None
    
    #create a room returning the room object
    @staticmethod
    def createRoom(roomName, superTournamentKey):
        #Generate a Key
        public = Room.generateKey()
        private = Room.generateKey(public)
        #Create a new room passing the key, name, and if it is live or not; id is auto generated
        room = Room(name=roomName, superTournament=superTournamentKey, privateKey=private,  publicKey=public, isLive=False)
        db.session.add(room)
        db.session.commit()
        return room
    #generates a unique key for the room: regardless of whether the key is intended to be public or private
    @staticmethod
    def generateKey(invalidKey=None):
        key = ""
        values = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        #Create a key while the key is empty or the key already exists
        while len(key) ==0 or Room.exists(key) or key == invalidKey:
            key = "" #reset key
            #create a key of 8 characters using lower and upper case letters and numbers
            #62^8=218,340,105,584,896 possible keys a lot
            while len(key) < 8:
                key += values[random.randint(0, len(values) - 1)]
        return key
    @staticmethod
    def getRoomByPrivate(privateKey):
        return db.session.query(Room).filter_by(privateKey=privateKey).first()
    @staticmethod
    def getRoomByPublic(publicKey):
        return db.session.query(Room).filter_by(publicKey=publicKey).first()
    @staticmethod
    def getRoom(key):
        return Room.getRoomByPrivate(key) or Room.getRoomByPublic(key)


class Team(db.Model):
    #id of the team
    id = db.Column(db.Integer, primary_key=True, unique=True)
    #used to join a team
    privateKey = db.Column(db.String(8), unique=True)
    publicKey = db.Column(db.String(8), unique=True)
    #name of the team
    name = db.Column(db.String(100), unique=False)
    #key of the super tournament
    superTournament = db.Column(db.String(8), db.ForeignKey('tournament.privateKey'))

    #official Players in the team: Max of 4
    player1 = db.Column(db.Integer, db.ForeignKey('player.privateKey'))
    player2 = db.Column(db.Integer, db.ForeignKey('player.privateKey'))
    player3 = db.Column(db.Integer, db.ForeignKey('player.privateKey'))
    player4 = db.Column(db.Integer, db.ForeignKey('player.privateKey'))
  
    players = db.relationship('Player', backref='team', lazy='dynamic', primaryjoin="or_(Team.privateKey==Player.superTeam)")
    #FUNCTIONS
    #serialize the team object by converting it to a dictionary; we do this so we can send it as a json object
    @property
    def serialize(self):
        return {
            'id': self.id,
            'publicKey': self.publicKey,
            'privateKey': self.privateKey,
            'name': self.name,
            'superTournament': self.superTournament,
            'player1': self.player1,
            'player2': self.player2,
            'player3': self.player3,
            'player4': self.player4
        }

    #STATIC FUNCTIONS
    #see if a team exsists
    @staticmethod
    def exists(key):
        privateTeam = db.session.query(Team).filter_by(publicKey=key).first()
        publicTeam = db.session.query(Team).filter_by(privateKey=key).first()
        return privateTeam != None or publicTeam != None
    #create a new team
    @staticmethod
    def createTeam(teamName, superTournamentKey):
        #Generate a Key
        public = Team.generateTeamKey()
        private = Team.generateTeamKey(public)
        #Create a new team passing the key, name, and if it is live or not; id is auto generated
        team = Team(name=teamName, superTournament=superTournamentKey, privateKey=private, publicKey=public)
        db.session.add(team)
        db.session.commit()
        return team
    #generates a unique key for the team and makes sure it is not the same as invlid key parameter passed
    @staticmethod
    def generateTeamKey(invalidKey=None):
        key = ""
        values = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        #Create a key while the key is empty or the key already exists
        while len(key) ==0 or Room.exists(key) or key == invalidKey:
            key = "" #reset key
            #create a key of 8 characters using lower and upper case letters and numbers
            #62^8=218,340,105,584,896 possible keys a lot
            while len(key) < 8:
                key += values[random.randint(0, len(values) - 1)]
        return key
    @staticmethod
    def getTeamByPrivate(privateKey):
        return db.session.query(Team).filter_by(privateKey=privateKey).first()
    @staticmethod
    def getTeamByPublic(publicKey):
        return db.session.query(Team).filter_by(publicKey=publicKey).first()
    
class Result(db.Model):
    #id of the result
    id = db.Column(db.Integer, primary_key=True, unique=True)
    #team that got the question right: Team ABCorD
    teamLetter = db.Column(db.String(1), unique=False)
    #player that got the question right: Player 1, 2, 3, or 4
    playerNumber = db.Column(db.String(1), unique=False)
    #room that the question was in
    superRoom = db.Column(db.Integer, db.ForeignKey('room.privateKey'))

    #QuestionNumber
    questionNumber = db.Column(db.Integer, unique=False)
    #has the question been answered?
    answered = db.Column(db.Boolean, unique=False)
    #tossup achieved?
    tossup = db.Column(db.Boolean, unique=False)
    tossupQuestion = db.Column(db.String(2000), unique=False, default="", nullable=False)
    #accepted answer
    tossupAnswer = db.Column(db.String(2000), unique=False, default="", nullable=False)
    #bonuses achieved?
    bonus1 = db.Column(db.Boolean, unique=False)
    bonus1Question = db.Column(db.String(2000), unique=False, default="", nullable=False)
        #accepted answer
    bonus1Answer = db.Column(db.String(2000), unique=False,default="", nullable=False)
    bonus2 = db.Column(db.Boolean, unique=False)
    bonus2Question = db.Column(db.String(2000), unique=False, default="", nullable=False)
        #accepted answer

    bonus2Answer = db.Column(db.String(2000), unique=False, default="", nullable=False)

    #calculate the total points
    @property
    def totalPoints(self):
        return 10 if self.tossup else 0 + 5 if self.bonus1 else 0 + 5 if self.bonus2 else 0
    #serialize the result object by converting it to a dictionary; we do this so we can send it as a json object
    @property
    def serialize(self):
        return {
            'id': self.id,
            'questionNumber': self.questionNumber,
            'teamLetter': self.teamLetter,
            'playerNum': self.playerNumber,
            'superRoom': self.superRoom,
            'tossup': self.tossup,
            'bonus1': self.bonus1,
            'bonus2': self.bonus2,
            'totalPoints': self.totalPoints, 
            'tossupQuestion': self.tossupQuestion if self.tossupQuestion != "None" else "",
            'bonus1Question': self.bonus1Question if self.tossupQuestion != "None" else "",
            'bonus2Question': self.bonus2Question if self.tossupQuestion != "None" else "", 
            'tossupAnswer': self.tossupAnswer if self.tossupQuestion != "None" else "",
            'bonus1Answer': self.bonus1Answer if self.tossupQuestion != "None" else "",
            'bonus2Answer': self.bonus2Answer if self.tossupQuestion != "None" else "",
            'answered': self.answered
        }


    