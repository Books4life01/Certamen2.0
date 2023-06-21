from website import create_app, createSocketServer
import socket

app = create_app()
socketio = createSocketServer(app)


#ensures that the app is run only when the main.py file is run not when it is imported
if __name__ == "__main__":
    socketio.run(app, debug=True, host=socket.gethostbyname(socket.gethostname()), port=8080)
