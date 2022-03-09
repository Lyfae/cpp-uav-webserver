# app.py
#referenced from https://stackabuse.com/deploying-a-flask-application-to-heroku/
import socket
import cv2
import pickle
import struct
import imutils
from flask import Flask, request, jsonify

app = Flask(__name__)

# A welcome message to test our server
@app.route('/')
def index():
    return "Welcome to the server"

def server():
    #create the socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # host_name = socket.gethostname()
    # host_ip = socket.gethostbyname(host_name)
    host_ip = 'local'

    #connection output status
    #print("Host IP:", host_ip)

    #set port and socket
    port = 9999
    socket_address = (host_ip,port)

    #binding the socket
    server_socket.bind(socket_address)

    #socket listen
    server_socket.listen(5)
    #print("Listening At: ",socket_address)

    client_socket,addr = server_socket.accept()
    print("Getting Connetion From:", addr)
    
    return "Got Connection Successful"





if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
