from flask_socketio import  emit
from .. import db
from ..models import Player, Tournament, Room, Team, Result

#On data Refresh Request
def on_tournDataRefreshRequest( message, brdcst=False):
    print(message)
    #retrieve tourn key: either public or private
    tournKey = message["tournKey"]
    tourn = Tournament.getTourn(tournKey)
    if tourn != None:
        #retrieve list of rooms(list of objects) from tournament object
        rooms = tourn.getRooms()
        #send room data to client
        print("Sending Rooms Data: brdcst" + str(brdcst))
        emit('roomsUpdate', {"tournKey":tournKey, "rooms":rooms}, broadcast=brdcst)
        print("Rooms Data Sent")
        #retrieve list of teams(list of objects) from tournament object
        teams = tourn.getTeams()
        emit('teamsUpdate', {"tournKey":tournKey, "teams":teams}, broadcast=brdcst)
    else:
        #do something
        emit("ERROR", "Tournament not found upon tournDataRefreshRequest")
def on_roomDataRefreshRequest(message, brdcst=False):
    #retrieve roomKey from request either public or private
    roomKey = message["roomKey"]
    room = Room.getRoom(roomKey)

    if room != None:
        tourn  = Tournament.getTourn(room.superTournament)
        #retrieve list of teams(list of objects) from tournament object
        teams = tourn.getTeams()
        #send data to client
        emit('tournTeamsUpdate', {"roomKey":roomKey, "teams":teams}, broadcast=brdcst)
        #retrieve list of teams(list of objects) from room object
        roomTeams = room.getTeams()
        emit('roomTeamsUpdate', {"roomKey":roomKey, "teams":roomTeams}, broadcast=brdcst)
        #retrieve list of results(list of objects) from room object
        results = room.getResults()
        outResults = {
            "roomKey": roomKey,
            "curQuestion": room.currentQuestion,
            "resultList": results,
        }
        emit('roomResultsUpdate', outResults, broadcast=brdcst)
    else:
        emit("ERROR", "Room not found upon roomDataRefreshRequest")
