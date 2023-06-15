from website import create_app
import socket

app = create_app()

#ensures that the app is run only when the main.py file is run not when it is imported
if __name__ == "__main__":
    app.run(debug=True, host=socket.gethostbyname(socket.gethostname()))