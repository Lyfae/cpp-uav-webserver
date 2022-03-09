# app.py
#referenced from https://stackabuse.com/deploying-a-flask-application-to-heroku/
import socket
import cv2
import pickle
import struct
import imutils
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/getmsg/', methods=['GET'])
def respond():
    # Retrieve the name from url parameter
    name = request.args.get("name", None)

    # For debugging
    print(f"got name {name}")

    response = {}

    # Check if user sent a name at all
    if not name:
        response["ERROR"] = "no name found, please send a name."
    # Check if the user entered a number not a name
    elif str(name).isdigit():
        response["ERROR"] = "name can't be numeric."
    # Now the user entered a valid name
    else:
        response["MESSAGE"] = f"Welcome {name} to our awesome platform!!"

    # Return the response in json format
    return jsonify(response)

@app.route('/post/', methods=['POST'])
def post_something():
    param = request.form.get('name')
    print(param)
    # You can add the test cases you made in the previous function, but in our case here you are just testing the POST functionality
    if param:
        return jsonify({
            "Message": f"Welcome {name} to our awesome platform!!",
            # Add this option to distinct the POST request
            "METHOD" : "POST"
        })
    else:
        return jsonify({
            "ERROR": "no name found, please send a name."
        })

# A welcome message to test our server
@app.route('/')
def index():
    #create the socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # host_name = socket.gethostname()
    # host_ip = socket.gethostbyname(host_name)
    host_ip = 'local'

    #connection output status
    print("Host IP:", host_ip)

    #set port and socket
    port = 9999
    socket_address = (host_ip,port)

    #binding the socket
    server_socket.bind(socket_address)

    #socket listen
    server_socket.listen(5)
    print("Listening At: ",socket_address)

    #socket accept
    try:
        while True:
            client_socket,addr = server_socket.accept()
            print("Getting Connetion From:", addr)
            #upon successful connection
            if client_socket:
                vid = cv2.VideoCapture(0)
                #while video feed is opened
                while(vid.isOpened()):
                    img,frame = vid.read()
                    frame = imutils.resize(frame,width=320)
                    a = pickle.dumps(frame)           
                    message = struct.pack("Q",len(a)) + a
                    client_socket.sendall(message)
                    cv2.imshow("Transmitting Video",frame)
                    key = cv2.waitKey(1) & 0xFF

                    #closing socket 
                    if key == ord('q'):
                        client_socket.close()
    except KeyboardInterrupt:
        pass



if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
