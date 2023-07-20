from flask_socketio import emit  
from .. import db   
from ..models import Player, Tournament, Room, Team, Result
from .. import liveRoomClients
from .refreshSocket import emitRoomResults, emitRoomData, emitRoomLiveQuestionUpdate, emitTournData

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
    emitTournData(room.superTournament, True)
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
        room.curQuestionType = message["curQuestionType"]
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
    # print("liveQuestionUpdate: " + data['actionType'])
    # print(data)
    #retrieve room
    roomPrivateKey = data["roomKey"]
    room = Room.getRoom(roomPrivateKey)

    #get result and question Type
    result = room.results[data["questionNum"]-1]
    questionType = data["questionType"]

    #get actionType
    actionType = data["actionType"]

    if actionType == "startBroadcast":
        #reset the curent live question
        room.curLiveQuestion = ""
        #reset the current live question answer
        room.curLiveQuestionAnswer = ""
        #reset the players who attempted
        room.clearAttemptedPlayers()
        #set the reuslts question to the live question
        if questionType == 0:result.tossupQuestion = data['fullQuestion']
        elif questionType == 1:result.bonus1Question = data['fullQuestion']
        elif questionType == 2:result.bonus2Question = data['fullQuestion']
    elif actionType == "endBroadcast":
        #set the stored question and answers to the live question and answer
        if questionType == 0:result.tossupAnswer = room.curLiveQuestionAnswer
        elif questionType == 1:result.bonus1Answer = room.curLiveQuestionAnswer
        elif questionType == 2:result.bonus2Answer = room.curLiveQuestionAnswer
        
    elif actionType == "nextChar":
        #add the next character to the live question
        room.curLiveQuestion += data['nextChar']
    elif actionType == "pause":
        room.liveQuestionPaused = True
        room.addAttemptedPlayer(data['player']['privateKey'])
    elif actionType == "attemptAnswer":
        room.curLiveQuestionAnswer = data['attemptedAnswer']
    elif actionType == "rejectAnswer":
        room.curLiveQuestionAnswer = ""
        room.curLiveQuestionPaused = False
    elif actionType == "acceptAnswer":
        #set the stored question and answers to the live question and answer
        result.curLiveQuestion = result.tossupQuestion
        if questionType == 0:result.tossupAnswer = room.curLiveQuestionAnswer
        elif questionType == 1:result.bonus1Answer = room.curLiveQuestionAnswer
        elif questionType == 2:result.bonus2Answer = room.curLiveQuestionAnswer
        
        
        room.liveQuestionPaused=False
    db.session.commit()
    #broadcast live question update to all clients connected to the room including
    if(actionType=="pause" or actionType=="attemptAnswer" ):
        emitRoomLiveQuestionUpdate(roomPrivateKey, data['actionType'], True, player =data['player'])
    else: emitRoomLiveQuestionUpdate(roomPrivateKey, data['actionType'], True)
    #if the actionType is acceptAnswer or endBroadcast then broadcast the room data
    if(actionType=="acceptAnswer" or actionType=="endBroadcast"):
        emitRoomData(roomPrivateKey, True)
        emitRoomResults(roomPrivateKey, True)

