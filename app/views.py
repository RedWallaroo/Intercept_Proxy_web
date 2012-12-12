from flask import *
from app import app
from config import UPDATED
import socket, sys, random, threading, time, os

from proxy import Server
import pdb

s = Server()

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
    pdb.set_trace()
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

    parent_r, parent_w = os.pipe()
    child_r, child_w = os.pipe()
    pid = os.fork()

    if pid:
        os.write(parent_w, 'start')
        while True:
            message_length = int(os.read(child_r, 10))
            message = os.read(child_r,message_length)
            if message.find("status:") == 0:
                response = {'status': message}
                break
            elif message.find("data:") == 0:
                response = {'data': message}
                return jsonify(response)
                action = raw_input("Continue? --> ")
                if action == 'c':
                    os.write(parent_w, 'c')
                elif action == 'd':
                    os.write(parent_w, 'd')
            else:
                pass
        return jsonify(response)
    else: # I'm the child
        instruction = os.read(parent_r, 99999)
        if instruction == 'start':
            s.run(parent_r, child_w)
        elif instruction == 'stop':
            s.stop()










