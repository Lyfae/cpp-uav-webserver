# app.py
#referenced from https://stackabuse.com/deploying-a-flask-application-to-heroku/

import socket
import cv2
import pickle
import struct
import imutils

from flask import Flask, request, jsonify
from flask import render_template
app = Flask(__name__)

# A welcome message to test our server
@app.route('/')
def index():
	# return the rendered template
	return "Hello"



if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
