from flask_socketio import emit
from flask import request

from website.routes.updateSocket import on_liveQuestionUpdate
from .. import db
from ..models import Player, Tournament, Room, Team, Result
from .. import liveRoomClients
from .refreshSocket import emitRoomData, on_roomDataRefreshRequest, on_tournDataRefreshRequest
#Manage Connection
# def on_connect():
    # print("Connected with sid of " + str(request.sid))
#Manage Disconnection
def on_disconnect():
    #retrive client object being disconnected
    socketClient = request.sid
    #loop through all live rooms
    keys = list(liveRoomClients.keys())
    for key in keys:
        room = liveRoomClients[key]
        if room["host"] == socketClient:
            #if the client is the host of the room
            roomObj = Room.getRoom(key)
            #send out a rejectAnswer message and clearTimer liveQuestion broadcast update
            on_liveQuestionUpdate(data = {"roomKey": roomObj.privateKey, "questionNum": roomObj.curQuestionNumber,"questionType": roomObj.curQuestionType, "actionType":"rejectAnswer","questionNum":roomObj.curQuestionNumber})
            #loop through all clients in the room
            for client in room["clients"]:
                #emit a disconnect message to all clients in the room
                emit('ERROR', "Host Disconnected", room=client['id'])
            #remove the room from the liveRoomClients dictionary
            liveRoomClients.pop(key)
            Room.getRoomByPublic(key).isLive = False
            db.session.commit()
            #send rooms update to all sockets
            on_tournDataRefreshRequest({"tournKey": Room.getRoomByPublic(key).superTournament}, brdcst=True)
        elif any(client for client in room["clients"] if client['id']==socketClient):
            #if the client is a client in the room
            client = next(client for client in room["clients"] if client['id']==socketClient)
            #remove the client from the room
            room["clients"].remove(client)
            #remove live player from room
            Room.getRoomByPublic(key).removeLivePlayer(client["playerKey"])
    # print(str(socketClient) + " Disconnected")
    # print("CUrrent Live ROoms")
    # print(liveRoomClients)
#Manage LiveRoom Connection
def on_roomHostConnect( message):
    #retrieve sid from request which is the socket id
    sid = request.sid
    #retrieve roomKey from request
    privateKey = message["roomKey"]
    #retrieve room object from database using roomKey
    room = Room.getRoomByPrivate(privateKey)
    if room == None:
        emit("ERROR", "Invalid Room Key")
        return
    #set the room to be live and commit the changes to the database

    room.isLive = True
    db.session.commit()
    #add the room to the liveRoomClients dictionary
    liveRoomClients[room.publicKey] = {
        "host": sid,
        "clients": []
    }
    # print("Host Joined: " + str(sid) + " to room: " + str(privateKey))
    # print("Current Live ROoms")
    # print(liveRoomClients)
    #broadcast room live update 
    on_tournDataRefreshRequest({"tournKey": room.superTournament}, brdcst=True)
def on_roomClientConnect( message):
    #retrieve sid from request which is the socket id
    sid = request.sid
    #retrieve public roomKey from request
    publicKey = message["roomKey"]
    room = Room.getRoomByPublic(publicKey)
    if room == None:
        emit("ERROR", "Invalid Room Key")
    else:
        #retrieve the privateKey
        #add the client to the room
        liveRoomClients[publicKey]["clients"].append({"id":sid, "playerKey":message["playerKey"]})
        #update the playerCount to the database
        for letter in ['A','B','C','D']:
            setattr(room, 'team' + letter + 'Players',0)
            for player in liveRoomClients[publicKey]["clients"]:
                player = Player.getPlayer(player["playerKey"])
                if player.superTeam == getattr(room, 'team' + letter):
                    setattr(room, 'team' + letter + 'Players',getattr(room, 'team' + letter + 'Players')+1)
        db.session.commit()
        print(liveRoomClients)
        emitRoomData(room.privateKey, brdcst=True)
