# # app.py
# #referenced from https://stackabuse.com/deploying-a-flask-application-to-heroku/

# from flask import Flask, render_template, request

# app = Flask(__name__)

# # A welcome message to test our server
# @app.route('/')
# def index():
# 	# return the rendered template
# 	return "Hello"



# if __name__ == '__main__':
    
#     app.run(debug=True, host='0.0.0.0')

from singleMD import SingleMotionDetector
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
import threading
import argparse
import datetime
import imutils
import time
import cv2
from http import client
import socket
import pickle
import struct
import numpy as np

#some global stuff
global data
global frame

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs
# are viewing the stream)
outputFrame = None
lock = threading.Lock()
# initialize a flask object
app = Flask(__name__,template_folder='templates')
# initialize the video stream and allow the camera sensor to
# warmup
#vs = VideoStream(usePiCamera=1).start()

#create socket
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
# host_ip = '192.168.1.11'
port = 9999

#connection
client_socket.connect((host_ip,port)) # this value is a tuple
data = b""
#Q unsigned long int that takes 8 bytes
payload_size = struct.calcsize("Q") #set as string

time.sleep(1.0)

@app.route("/")
def index():
	# return the rendered template
	return render_template("index.html")

def detect_motion(frameCount):
	# grab global references to the video stream, output frame, and
	# lock variables
	global outputFrame, lock,data
	# initialize the motion detector and the total number of frames
	# read thus far
	md = SingleMotionDetector(accumWeight=0.1)
	total = 0
	while True:
		while len(data) < payload_size:
			#receiving the packets and appending them into the data
			packet = client_socket.recv(4*1024) #4k of byte buffer
			if not packet:
				break

			#adding packet to data
			data += packet
		#first 8 bytes contain size of packet message 
		packed_msg_size = data[:payload_size]
		#rest of data contains video frame
		data = data[payload_size:]
		msg_size = struct.unpack("Q",packed_msg_size)[0]

		#looping til we receive all the data from the frame
		while len(data) < msg_size:
			data += client_socket.recv(4*1024)

		#frame data is recovered
		frame_data = data[:msg_size]
		data = data[msg_size:]
		frame = pickle.loads(frame_data)
		
		# loop over frames from the video stream
		# read the next frame from the video stream, resize it,
		# convert the frame to grayscale, and blur it
		frame = imutils.resize(frame, width=400)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (7, 7), 0)
		# grab the current timestamp and draw it on the frame
		timestamp = datetime.datetime.now()
		cv2.putText(frame, timestamp.strftime(
			"%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
			cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

		# if the total number of frames has reached a sufficient
		# number to construct a reasonable background model, then
		# continue to process the frame
		if total > frameCount:
			# detect motion in the image
			motion = md.detect(gray)
			# check to see if motion was found in the frame
			if motion is not None:
				# unpack the tuple and draw the box surrounding the
				# "motion area" on the output frame
				(thresh, (minX, minY, maxX, maxY)) = motion
				cv2.rectangle(frame, (minX, minY), (maxX, maxY),
					(0, 0, 255), 2)
		
		# update the background model and increment the total number
		# of frames read thus far
		md.update(gray)
		total += 1
		# acquire the lock, set the output frame, and release the
		# lock
		with lock:
			outputFrame = frame.copy()

def generate():
	# grab global references to the output frame and lock variables
	global outputFrame, lock
	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if outputFrame is None:
				continue
			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
			# ensure the frame was successfully encoded
			if not flag:
				continue
		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')


@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

# check to see if this is the main thread of execution
if __name__ == '__main__':
	# construct the argument parser and parse command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=False,
        help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=False,
        help="ephemeral port number of the server (1024 to 65535)")
    ap.add_argument("-f", "--frame-count", type=int, default=32,
        help="# of frames used to construct the background model")
    args = vars(ap.parse_args())
    # start a thread that will perform motion detection
    t = threading.Thread(target=detect_motion, args=(
        args["frame_count"],))
    t.daemon = True
    t.start()
    app.run(threaded=True, port=5000)
    
