from flask_socketio import emit
from flask import request
from .. import db
from ..models import Player, Tournament, Room, Team, Result
from .. import liveRoomClients
#Manage Connection
def on_connect():
    print("Connected with sid of " + str(request.sid))
#Manage Disconnection
def on_disconnect():
    #retrive client object being disconnected
    client = request.sid
    #loop through all live rooms
    for room in liveRoomClients:
        if room["host"] == client:
            #if the client is the host of the room
            #loop through all clients in the room
            for client in room["clients"]:
                #emit a disconnect message to all clients in the room
                emit('disconnect', room=room["roomKey"], namespace="/")
            #remove the room from the liveRoomClients dictionary
            liveRoomClients.pop(room["roomKey"])
        elif client in room["clients"]:
            #if the client is a client in the room
            #remove the client from the room
            room["clients"].remove(client)
    print(str(client) + " Disconnected")
#Manage LiveRoom Connection
def on_roomHostConnect( message):
    #retrieve sid from request which is the socket id
    sid = request.sid
    #retrieve roomKey from request
    privateKey = message["publicKey"]
    #retrieve room object from database using roomKey
    room = Room.query.filter_by(privateKey=privateKey).first()
    #set the room to be live
    room.isLive = True
    #add the room to the liveRoomClients dictionary
    liveRoomClients[room.publicKey] = {
        "host": sid,
        "clients": []
    }
def on_roomClientConnect( message):
    #retrieve sid from request which is the socket id
    sid = request.sid
    #retrieve public roomKey from request
    publicKey = message["publicKey"]
    liveRoomClients[publicKey]["clients"].append(sid)