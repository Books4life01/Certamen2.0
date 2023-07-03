from flask_socketio import emit  
from .. import db   
from ..models import Player, Tournament, Room, Team, Result
from .. import liveRoomClients

def on_teamAssignmentUpdate( message):
    #retrieve room Private Key
    roomPrivateKey = message["roomKey"]
    #retrive team assignments by teamPrivateKeys
    teamA,teamB,teamC,teamD = message["teamA"],message["teamB"],message["teamC"],message["teamD"]
    room = Room.getRoomByPrivate(roomPrivateKey)
    if room is None:
        emit("ERROR", "No room found with that private key")
    else:
        room.teamA = teamA
        room.teamB = teamB
        room.teamC = teamC
        room.teamD = teamD
        db.session.commit()
    #TO-DO: send Updated team assignment to any clients connected to the room
def on_roomResultUpdate( message):
    #retrieve request data
    roomPrivateKey = message["roomKey"]
    room = Room.getRoomByPrivate(roomPrivateKey)
    if room is None:
        emit("ERROR", "No room found with that private key")
    else:
        questionNum = message["questionNum"]
        
        #retrieve Results list from room
        results = room.results
        
        #if the result number doesnt exsist yet create it 
        if(len(results) < questionNum):
            room.addResult(message["teamLetter"],message["playerNum"],questionNum, message["tossup"], message["bonus1"], message["bonus2"])
        else:
            #otherwise update the result
            room.results[questionNum-1].tossup = message["tossup"]
            room.results[questionNum-1].bonus1 = message["bonus1"]
            room.results[questionNum-1].bonus2 = message["bonus2"]
            room.results[questionNum-1].teamLetter = message["teamLetter"]
            room.results[questionNum-1].playerNumber = message["playerNum"]
            room.results[questionNum-1].questionNum = questionNum
        db.session.commit()
def on_roomCurQuestionUpdate( message):
    #retrieve request data
    roomPrivateKey = message["roomKey"]
    room = Room.getRoomByPrivate(roomPrivateKey)
    if room is None:
        emit("ERROR", "No room found with that private key")
    else:
        room.curQuestion = message["curQuestion"]
        db.session.commit()