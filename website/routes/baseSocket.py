from flask_socketio import emit
from flask import request
from .. import db
from ..models import Player, Tournament, Room, Team, Result
from .. import liveRoomClients
from .refreshSocket import on_roomDataRefreshRequest, on_tournDataRefreshRequest
#Manage Connection
def on_connect():
    print("Connected with sid of " + str(request.sid))
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
            #loop through all clients in the room
            for client in room["clients"]:
                #emit a disconnect message to all clients in the room
                emit('disconnect', room=key, namespace="/")
            #remove the room from the liveRoomClients dictionary
            liveRoomClients.pop(key)
            Room.getRoomByPublic(key).isLive = False
            db.session.commit()
            #send rooms update to all sockets
            on_tournDataRefreshRequest({"tournKey": Room.getRoomByPublic(key).superTournament}, brdcst=True)
        elif socketClient in room["clients"]:
            #if the client is a client in the room
            #remove the client from the room
            room["clients"].remove(socketClient)
    print(str(socketClient) + " Disconnected")
    print("CUrrent Live ROoms")
    print(liveRoomClients)
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
    print("Host Joined: " + str(sid) + " to room: " + str(privateKey))
    print("Current Live ROoms")
    print(liveRoomClients)
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
        liveRoomClients[publicKey]["clients"].append(sid)