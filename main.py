from website import create_app, createSocketServer, ip
import socket
import os


app = create_app()
socketio = createSocketServer(app)
# Add the Cache-Control and Pragma headers to the response
@app.after_request
def add_header(response):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response


#ensures that the app is run only when the main.py file is run not when it is imported
if __name__ == "__main__":
    # os.environ['PYTHONDONTWRITEBYTECODE'] = '0'
    # os.system("python -m compileall -b -f -o ./__pycache__ ./")
    print("Current Host: " + socket.gethostbyname(socket.gethostname()))
    print("Starting server... on " + ip)
    socketio.run(app, debug=True, host=(ip.replace("http://", "").replace(":8080", "")), port=8080)
