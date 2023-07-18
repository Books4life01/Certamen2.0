from flask_socketio import emit  
from .. import db   
from ..models import Player, Tournament, Room, Team, Result
from .. import liveRoomClients
from .refreshSocket import emitRoomResults, emitRoomData, emitRoomLiveQuestionUpdate

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
    print("liveQuestionUpdate: " + data['actionType'])
    print(data)
    #retrieve room
    roomPrivateKey = data["roomKey"]
    room = Room.getRoomByPrivate(roomPrivateKey)

    #get result and question Type
    result = room.results[data["questionNum"]-1]
    questionType = data["questionType"]

    #get actionType
    actionType = data["actionType"]

    if actionType == "startBroadcast":
        #reset the curent live question
        room.curLiveQuestion = ""
        #reset the current live question answer
        room.liveQuestionAnswer = ""
        #reset the players who attempted
        room.clearAttemptedPlayers()
        #set the reuslts question to the live question
        result.tossupQuestion = data['fullQuestion']
    elif actionType == "endBroadcast":
        #set the stored question and answers to the live question and answer
        result.tossupQuestion = room.curLiveQuestion
        result.tossupAnswer = room.curLiveQuestionAnswer
    elif actionType == "nextChar":
        #add the next character to the live question
        room.curLiveQuestion += data['nextChar']
    elif actionType == "pause":
        room.liveQuestionPaused = True
    elif actionType == "attemptAnswer":
        room.addAttemptedPlayer(data['playerKey'])
        room.liveQuestionAnswer = data['attemptedAnswer']
    elif actionType == "rejectAnswer":
        room.liveQuestionAnswer = ""
        room.liveQuestionPaused = False
    elif actionType == "acceptAnswer":
        #set the stored question and answers to the live question and answer
        result.tossupQuestion = room.curLiveQuestion
        result.tossupAnswer = room.curLiveQuestionAnswer
    db.session.commit()
    #broadcast live question update to all clients connected to the room including
    emitRoomLiveQuestionUpdate(roomPrivateKey, data['actionType'], True)

    

    data['roomKey'] = room.publicKey
    if room is None or not room.isLive:
        emit("ERROR", "No room found with that private key")
    else:
        print("Sending live question update")
        emit("incomingQuestion", data, broadcast=True, includes_self=True)
        emitRoomData(roomPrivateKey, True)

