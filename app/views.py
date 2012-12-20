from flask import *
from httplib import *
from app import app
from config import UPDATED
import socket, sys, random, threading, time, os

from proxy import Server
import pdb

s = Server()
isRunning = False
pid = ""
parent_r = ""
parent_w = ""
child_r = ""
child_w = ""

@app.route("/data", methods=['GET'])
def data():
    #Source for AJAX queries
    #fmt = request.args.get('format', 'best') # gets query params
    status_msg = "status"
    request_bar = "http://address.com"
    raw_request = "HTTP:// 1.1 GET http://address.com"

    response = {'status': status_msg,
                'request_bar' : request_bar,
                'raw_request' : raw_request
                }

    return jsonify(response)

@app.route("/updated")
def updated():
    # Wait until something has changed and report it.
    # Uses check-sleep loop to wait for an update.
    empty = s.q.empty()
    while s.q.empty():
        time.sleep(0.5)
    return "changed!"



@app.route('/')
@app.route('/index', methods = ['GET', 'POST'])
def index():
    return render_template("index.html")

@app.route('/start', methods = ['GET', 'POST'])
def start():
    parent_action = 'start'
    status = synchronizer(parent_action)
    #return jsonify(status)
    return status


@app.route('/stop', methods = ['GET', 'POST'])
def stop():
    parent_action = 'stop'
    status = synchronizer(parent_action)
    #return jsonify(status)
    return status

@app.route('/update', methods = ['GET', 'POST'])
def update():
    parent_action = "update"
    data = synchronizer(parent_action)
    #return jsonify(data)
    return data

@app.route('/forward', methods = ['GET', 'POST'])
def forward():
    parent_action = "forward"
    data = synchronizer(parent_action)
    #return jsonify(data)
    return data


@app.route('/drop', methods = ['GET', 'POST'])
def drop():
    parent_action = "drop"
    data = synchronizer(parent_action)
    #return jsonify(data)
    return data

def synchronizer(parent_action):
    #sychronizer starts and stops proxy.py
    global isRunning, parent_w, parent_r, child_w, child_r, pid
    if isRunning == False:
        parent_r, parent_w = os.pipe()
        child_r, child_w = os.pipe()
        pid = os.fork()
        isRunning = True
        print pid

    if pid: # Parent (Flask app) process here
        if parent_action == 'start':
            message = 'start'
            msglen = msg_len(message)
            os.write(parent_w, msglen + message)
        elif parent_action == 'stop':
            message = 'stop'
            msglen = msg_len(message)
            os.write(parent_w, msglen + message)
        elif parent_action == 'forward':
            message = 'forward'
            msglen = msg_len(message)
            os.write(parent_w, msglen + message)
        elif parent_action == 'drop':
            message = 'drop'
            msglen = msg_len(message)
            os.write(parent_w, msglen + message)
        response = check_for_message(child_r, parent_w)
        return response
    else: # Child (proxy.py) process here
        message_length = int(os.read(parent_r, 10))
        child_action = os.read(parent_r, message_length)
        # Process calls for proxy.py
        if child_action == 'start':
            s.run(parent_r, child_w)
            return
        elif child_action == 'stop':
            s.stop(parent_r, child_w)
            return

def check_for_message(child_r, parent_w):

    message_length = int(os.read(child_r, 10))
    message = os.read(child_r,message_length)
    response = ""

    if message.find("status:") == 0:
        #response = {'status': message}
        response = message
    elif message.find("data:") == 0:
        #response = {'data': message[5:]}
        response = message
    elif message.find("response:") == 0:
        #response = {'data' : message[9:]}
        response = message
    else:
        #response = {'empty':'empty'}
        response =  'empty:'
    return response


def msg_len(message):
    message_length = str(len(message))
    while len(message_length) != 10:
        message_length += " "
    return message_length



