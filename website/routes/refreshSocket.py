import json
from flask_socketio import  emit
from .. import db
from ..models import Player, Tournament, Room, Team, Result
from .. import liveRoomClients
#On data Refresh Request
def on_tournDataRefreshRequest( message, brdcst=False):
    print(message)
    #retrieve tourn key: either public or private
    tournKey = message["tournKey"]
    tourn = Tournament.getTourn(tournKey)
    if tourn != None:
        emitTournData(tournKey, brdcst)
        #send all the rooms from the tournament to the client
        emitTournRooms(tournKey, brdcst)
        #send all the teams from the tournament to the client
        emitTournTeams(tournKey, brdcst)
    else:
        #do something
        emit("ERROR", "Tournament not found upon tournDataRefreshRequest")
def on_roomDataRefreshRequest(message, brdcst=False):
    #retrieve roomKey from request either public or private
    roomKey = message["roomKey"]
    room = Room.getRoom(roomKey)

    if room != None:
        #emit room specific data
        emitRoomData(roomKey, brdcst)
        #send all the teams from the tournament to the client
        emitTournTeams(room.superTournament, brdcst)
        #send all the teams selected for  the room to the client
        emitRoomSelectedTeams(roomKey, brdcst)
        #send all the results from the room to the client
        emitRoomResults(roomKey, brdcst)
       
    else:
        emit("ERROR", "Room not found upon roomDataRefreshRequest")
#HELPER
def emitRoomResults(roomKey, brdcst):
    room = Room.getRoom(roomKey)
    #retrieve list of results(list of objects) from room object
    results = room.getResults()
    outResults = {
        "roomKey": roomKey,
        "resultList": results,
    }
    emit('roomResultsUpdate', outResults, broadcast=brdcst)
def emitTournTeams(tournKey, brdcst):
    tourn = Tournament.getTourn(tournKey)
    #retrieve list of teams(list of objects) from tournament object
    teams = tourn.getTeams()
    emit('tournTeamsUpdate', {"tournKey":tournKey, "teams":teams}, broadcast=brdcst)
def emitRoomSelectedTeams(roomKey, brdcst):
        #retrieve list of teams(list of objects) from room object
        room = Room.getRoom(roomKey)
        roomTeams = room.getTeams()
        emit('roomTeamsUpdate', {"roomKey":roomKey, "teams":roomTeams}, broadcast=brdcst)
def emitTournRooms(tournKey, brdcst):
    tourn = Tournament.getTourn(tournKey)
    #retrieve list of rooms(list of objects) from tournament object
    rooms = tourn.getRooms()
    emit('tournRoomsUpdate', {"tournKey":tournKey, "rooms":rooms}, broadcast=brdcst)
def emitRoomData(roomKey, brdcst):
    room = Room.getRoom(roomKey)
    emit('roomDataUpdate', room.serialize, broadcast=brdcst, include_self=True)
    emit('roomParticipantUpdate', {"privateKey":room.privateKey,"publicKey":room.publicKey, "participants":json.dumps(list(map(lambda client: {"playerKey":client['playerKey'], "teamKey":Player.getPlayer(client["playerKey"]).superTeam, "name":Player.getPlayer(client['playerKey']).name},liveRoomClients[room.publicKey]["clients"])))if room.publicKey in liveRoomClients else []}, broadcast=brdcst, include_self=True)
def emitTournData(tournKey, brdcst):
    tourn = Tournament.getTourn(tournKey)
    emit('tournDataUpdate', tourn.serialize, broadcast=brdcst)
def emitRoomLiveQuestionUpdate(roomKey, actionType, brdcst, player="None", extraData={}):
    room = Room.getRoom(roomKey)
    roomData = room.serialize
    emit('roomLiveQuestionUpdate', {"privateKey":room.privateKey,"publicKey":room.publicKey, "curLiveQuestion":roomData["curLiveQuestion"], "curLiveQuestionAnswer":roomData["curLiveQuestionAnswer"], "liveQuestionPaused":roomData["timer"]>0, "curQuestionType":roomData["curQuestionType"], "curQuestion":roomData["curQuestionNumber"], "playersAttempted":roomData["playersAttempted"], "actionType":actionType, "playerInitiated":player, "timer":roomData['timer'], "clientInfo":roomData['clientInfo'], "hostInfo":roomData['hostInfo'],"clientInfo":roomData['clientInfo']}, broadcast=brdcst, include_self=True)
    
