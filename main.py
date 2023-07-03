from website import create_app, createSocketServer
import socket
import os

app = create_app()
socketio = createSocketServer(app)


#ensures that the app is run only when the main.py file is run not when it is imported
if __name__ == "__main__":
    # os.environ['PYTHONDONTWRITEBYTECODE'] = '0'
    # os.system("python -m compileall -b -f -o ./__pycache__ ./")
    socketio.run(app, debug=True, host=socket.gethostbyname(socket.gethostname()), port=8080)
