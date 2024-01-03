from flask_socketio import emit  
from .. import db   
from ..models import Player, Tournament, Room, Team, Result
from .. import liveRoomClients
from .refreshSocket import emitRoomResults, emitRoomData, emitRoomLiveQuestionUpdate, emitRoomSelectedTeams, emitTournData, emitTeamData


def on_teamAssignmentUpdate( message):
    #retrieve room Private Key
    roomPrivateKey = message["roomKey"]
    #eretrive team assignments by teamPrivateKeys
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
    emitRoomSelectedTeams(roomPrivateKey, True)

    emitTournData(room.superTournament, True)
def on_roomResultUpdate(message):
    print("roomResultUpdate: ")
    print(message)
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
            room.addResult(message["teamAnsweredKey"],message["playerAnsweredKey"],questionNum, message["tossup"], message["bonus1"], message["bonus2"])
        else:
            #otherwise update the result
            room.results[questionNum-1].tossup = message["tossup"]
            room.results[questionNum-1].bonus1 = message["bonus1"]
            room.results[questionNum-1].bonus2 = message["bonus2"]
            room.results[questionNum-1].teamAnsweredKey = message["teamAnsweredKey"]
            room.results[questionNum-1].playerAnsweredKey = message["playerAnsweredKey"]
            room.results[questionNum-1].questionNum = questionNum
            room.results[questionNum-1].roomKey = message["roomKey"]
        db.session.commit()
    #braodcast result update to all clients connected to the room
    emitRoomResults(roomPrivateKey, True)

def on_roomCurQuestionNumberOrTypeUpdate(message):
    room = Room.getRoomByPrivate(message["roomKey"])
    if room is None:
        emit("ERROR", "No room found with that private key")
    else:
        #update the room's current question number and type
        try:
            room.curQuestionNumber = message["curQuestion"]
        except:
            pass
        try:
            room.curQuestionType = message["curQuestionType"]
        except:
            pass
        #update the room's current live question and answer
        if room.curQuestionNumber < len(room.results) and [room.results[room.curQuestionNumber-1].tossupQuestion, room.results[room.curQuestionNumber-1].bonus2Question, room.results[room.curQuestionNumber-1].bonus2Question][room.curQuestionType] != "":#if this next question has already been asked
            result = room.results[room.curQuestionNumber-1]
            if [result.tossupAnswer, result.bonus2Answer, result.bonus2Answer][room.curQuestionType] != "":#and if the answer has already been revealed
                room.clientInfo = Player.getPlayer(result.playerAnsweredKey).name + " got the answer correct!"
                room.hostInfo = Player.getPlayer(result.playerAnsweredKey).name + " got the answer correct!"
                room.curLiveQuestion = [result.tossupQuestion, result.bonus1Question, result.bonus2Question][room.curQuestionType]
                room.curLiveQuestionAnswer = [result.tossupAnswer, result.bonus1Answer, result.bonus2Answer][room.curQuestionType]
                print("THE QUESTION HAS BEEN ANSWERED ALREADU")
            else:#if the answer has not been revealed
                room.clientInfo = "Press Space to Buzz In"
                room.hostInfo = "Live Results"
                room.curLiveQuestion = [result.tossupQuestion, result.bonus1Question, result.bonus2Question][room.curQuestionType]
                room.curLiveQuestionAnswer = ""
            print("THE QUESTION HAS BEEN asked already")
        else:#if this next question has not been asked yet
            room.clientInfo = "Press Space to Buzz In"
            room.hostInfo = "Live Results"
            room.curLiveQuestion = ""
            room.curLiveQuestionAnswer = ""
        db.session.commit()
        emitRoomData(message["roomKey"], True)




    


def on_liveQuestionUpdate(data):
    print("liveQuestionUpdate: " + data['actionType'])
    print(data)
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
       
        #update clientInfo
        room.clientInfo = 'Press Space to Buzz In'
        room.hostInfo = 'Live Results'
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
    #for all these timer actions, the time left on the timer and the player who initiated the timer is sent to the client
    elif actionType == "startTimer" or actionType == "updateTimer" or actionType == "endTimer":
        room.clientInfo = "Submit Answer In: " + str(data['timeLeft']) + " seconds"
        room.hostInfo = data['playerInitiated']['name'] + " buzzed! They must Submit Answer In: " + str(data['timeLeft']) + " seconds"
        room.timer = data['timeLeft'] if not actionType == "endTimer" else 0
    elif actionType == "infoUpdate":
        room.clientInfo = data['clientInfo']
        room.hostInfo = data['hostInfo']
    elif actionType == "pause":
        room.addAttemptedPlayer(data['playerInitiated']['privateKey'])
    elif actionType == "attemptAnswer":
        room.curLiveQuestionAnswer = data['attemptedAnswer']
        room.hostInfo = data['playerInitiated']['name'] + "'s Answer: "
        room.clientInfo = data['playerInitiated']['name'] + "'s Answer: "
        room.timer = 0
     
    elif actionType == "rejectAnswer":
        room.curLiveQuestionAnswer = ""
        room.curLiveQuestionPaused = False
        room.clientInfo = "Answer Rejected. Press Space to Buzz In"
        room.hostInfo = "Live Results"
    elif actionType == "acceptAnswer":
        #set the stored question and answers to the live question and answer
        if questionType == 0:
            result.tossupAnswer = room.curLiveQuestionAnswer
            result.tossupQuestion = room.curLiveQuestion
        elif questionType == 1:
            result.bonus1Answer = room.curLiveQuestionAnswer
            result.bonus1Question = room.curLiveQuestion
        elif questionType == 2:
            result.bonus2Question = room.curLiveQuestion
            result.bonus2Answer = room.curLiveQuestionAnswer
        #set result's player and team answered values
        player = Player.getPlayer(list(filter(lambda x: x!="",room.getAttemptedPlayers()))[-1])
        result.playerAnsweredKey = player.privateKey
        result.teamAnsweredKey = player.superTeam
    db.session.commit()
    #broadcast live question update to all clients connected to the room including
    if(actionType=="pause" or actionType=="attemptAnswer" or actionType =="startTimer" or actionType =="updateTimer" or actionType =="endTimer" ):
        emitRoomLiveQuestionUpdate(roomPrivateKey, data['actionType'], True, player =data['playerInitiated'])
    else: emitRoomLiveQuestionUpdate(roomPrivateKey, data['actionType'], True)
    #if the actionType is acceptAnswer or endBroadcast then broadcast the room data
    if(actionType=="acceptAnswer" or actionType=="endBroadcast" or actionType=="startBroadcast" or actionType=="rejectAnswer"):
        emitRoomData(roomPrivateKey, True)
        emitRoomResults(roomPrivateKey, True)
def on_teamMemberAssignmentUpdate(data):
    team = Team.getTeamByPrivate(data['teamKey'])
    if data["Num"]==1:
        team.player1 = data['playerKey']
    elif data["Num"]==2:
        team.player2 = data['playerKey']
    elif data["Num"]==3:
        team.player3 = data['playerKey']
    elif data["Num"]==4:
        team.player4 = data['playerKey']
    db.session.commit()
    emitTournData(team.superTournament, True)
    #send a room selected teams update to all rooms in the tourn
    for room in Tournament.getTourn(team.superTournament).getRooms():
        emitRoomSelectedTeams(room["privateKey"], True)
    emitTeamData(data['teamKey'], False)

