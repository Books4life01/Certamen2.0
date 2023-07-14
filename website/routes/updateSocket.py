from flask_socketio import emit  
from .. import db   
from ..models import Player, Tournament, Room, Team, Result
from .. import liveRoomClients
from .refreshSocket import emitRoomResults, emitRoomData

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
    emitRoomData(roomPrivateKey, True)
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
            print(message)
            #otherwise update the result
            room.results[questionNum-1].tossup = message["tossup"]
            room.results[questionNum-1].bonus1 = message["bonus1"]
            room.results[questionNum-1].bonus2 = message["bonus2"]
            room.results[questionNum-1].teamLetter = message["teamLetter"]
            room.results[questionNum-1].playerNumber = message["playerNum"]
            room.results[questionNum-1].questionNum = questionNum
            room.results[questionNum-1].roomKey = message["roomKey"]
            room.results[questionNum-1].tossupQuestion = message["tossupQuestion"]
            room.results[questionNum-1].bonus1Question = message["bonus1Question"]
            room.results[questionNum-1].bonus2Question = message["bonus2Question"]
            room.results[questionNum-1].tossupAnswer = message["tossupAnswer"]
            room.results[questionNum-1].bonus1Answer = message["bonus1Answer"]
            room.results[questionNum-1].bonus2Answer = message["bonus2Answer"]
        db.session.commit()
    #braodcast result update to all clients connected to the room
    emitRoomResults(roomPrivateKey, True)
def on_roomCurQuestionAnswerStateUpdate(message):
    room = Room.getRoomByPrivate(message["roomKey"])
    if room is None:
        emit("ERROR", "No room found with that private key")
    else:
        room.results[message["curQuestion"]-1].answered = message["answered"]
    #broadcast result update to all clients connected to the room
    emitRoomData(message["roomKey"], True)
    
def on_roomCurQuestionTypeUpdate(message):
    room = Room.getRoomByPrivate(message["roomKey"])
    if room is None:
        emit("ERROR", "No room found with that private key")
    else:
        room.results[message["curQuestion"]-1].curQuestionType = message["curQuestionType"]
        db.session.commit()
    #broadcast result update to all clients connected to the room
    emitRoomData(message["roomKey"], True)
def on_roomCurQuestionUpdate( message):
    #retrieve request data
    roomPrivateKey = message["roomKey"]
    room = Room.getRoomByPrivate(roomPrivateKey)
    if room is None:
        emit("ERROR", "No room found with that private key")
    else:
        room.currentQuestion = message["curQuestion"]
        db.session.commit()
    emitRoomData(message["roomKey"], True)


def on_liveQuestionUpdate(data):
    print("liveQuestionUpdate")
    print(data)
    #retrieve request data
    roomPrivateKey = data["roomKey"]
    room = Room.getRoomByPrivate(roomPrivateKey)
    print(len(room.results))

    result = room.results[data["questionNum"]-1]

    questionType = data["questionType"]
    if questionType == 0:
        result.tossupQuestion = data["questionText"]
    elif questionType == 1:
        result.bonus1Question = data["questionText"]
    elif questionType == 2:
        result.bonus2Question = data["questionText"]
    db.session.commit()
    

    data['roomKey'] = room.publicKey
    if room is None or not room.isLive:
        emit("ERROR", "No room found with that private key")
    else:
        print("Sending live question update")
        emit("incomingQuestion", data, broadcast=True)
        emitRoomData(roomPrivateKey, True)
        