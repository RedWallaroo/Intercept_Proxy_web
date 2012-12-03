from flask import *
from app import app
from config import UPDATED
import socket, sys, random, threading, time

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

@app.route("/start")
def start():
    s.run()
    return jsonify("started!")






