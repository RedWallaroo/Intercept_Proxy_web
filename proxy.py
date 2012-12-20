import socket, sys, os, pdb, time, json
import Queue
import threading

# Importing HTTP_PARSER to get destination host from HTTP Request
# try to import C parser then fallback in pure python parser.
try:
    from http_parser.parser import HttpParser
except ImportError:
    from http_parser.pyparser import HttpParser

isAvailable = True


def msg_len(message):

    message_length = str(len(message))
    try:
        int(message_length)
    except:
        pdb.set_trace()
    while len(message_length) != 10:
        message_length += " "
    return message_length

def check_for_response(parent_r):
    while True:
        message_length = int(os.read(parent_r, 10))
        message = os.read(parent_r,message_length)
        response = ""
        if message == 'forward' or message == 'drop':
            response = message
            return response
        else:
            time.sleep(0.5)

class Server:
    def __init__(self):
        self.threads = []
        self.localhost = '0.0.0.0'
        self.port = 8080
        self.max = 999999
        self.q = Queue.Queue(maxsize=0)
        self.parent_r = ''
        self.child_w = ''
        self.isRunning = False
        self.Listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Listener_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self, parent_r, child_w):
        try:
            self.Listener_socket.bind((self.localhost, self.port))
            self.Listener_socket.listen(50)
            message = "status: listening on socket"
            msglen = msg_len(message)
            os.write(child_w, msglen + message)

        except socket.error, (value, message):
            if self.Listener_socket:
                self.Listener_socket.close()
            message = "status: error opening socket"
            msglen = msg_len(message)
            os.write(child_w, msglen + message)
            #print "error opening socket"
            self.Listener_socket.close()
            sys.exit(1)

    def stop(self, parent_r, child_w):
        try:
            self.isRunning = False
            self.Listener_socket.close()
            message = "status: listener socket closed"
            msglen = msg_len(message)
            os.write(child_w, msglen + message)
            sys.exit(1)
        except:
            message = "status: error closing socket"
            msglen = msg_len(message)
            os.write(child_w, msglen + message)
            sys.exit(1)

    def run(self, parent_r, child_w):
        self.start(parent_r, child_w)
        message = "status: waiting for connection"
        msglen = msg_len(message)
        os.write(child_w, msglen + message)
        #print "waiting for connection"
        isFirst = True
        self.isRunning = True
        while self.isRunning:
            threadObj = Client(self.Listener_socket.accept(), parent_r, child_w)
            t = ThreadQueue()
            t.add(threadObj, self.q)
            th = ThreadHandler(self.q)
            th.run()
        #print "error"
        message = "status: closing connections"
        msglen = msg_len(message)
        os.write(child_w, msglen + message)
        #print "closing connection"
        self.isRunning = False
        self.Listener_socket.close()
        t.shutdown()

class ThreadQueue():

    def __init__(self):
        pass

    def add(self, threadObj, q):
        self.q = q
        self.q.put(threadObj)

class ThreadHandler():

    def __init__(self, q):
        self.q = q

    def run(self):
        global isAvailable
        while self.q.empty() == False:
            if  isAvailable:
                threadObj = self.q.get()
                threadObj.start()
                isAvailable = False
            else:
                pass

class Client(threading.Thread):

    def __init__(self,(client, address), parent_r, child_w):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.max = 999999
        self.parent_r = parent_r
        self.child_w = child_w


    def run(self):

        self.client.settimeout(0.8)
        HTTP_Request = ""
        p = HttpParser()
        header_done = False
        destination_host = ''
        global isAvailable

        while True:
            try:
                Requestline = self.client.recv(self.max)
                if  Requestline != "":
                    HTTP_Request += Requestline
                else:
                    break
            except socket.timeout, socket.error:
                #message = 'status: request timeout or socket error'
                #msglen = msg_len(message)
                #os.write(self.child_w, msglen + message)
                #print "request timeout OR socket error"
                break
            except IOError:
                print "ioerror"
                break

            finally:
                if not HTTP_Request == "":
                    #print 'Got something from ' + str(self.address) + '...'
                    message = 'status: Got something from ' + str(self.address) + '...'
                    msglen = msg_len(message)
                    os.write(self.child_w, msglen + message)
                    request_length = len(HTTP_Request)
                    nparsed = p.execute(HTTP_Request, request_length)
                    assert nparsed == request_length

                    if p.is_headers_complete() and not header_done:
                        destination_host = p.get_headers()['Host']
                        header_done = True
                        message = 'data:' + HTTP_Request
                        msglen = msg_len(message)
                        os.write(self.child_w, msglen + message)
                        response = check_for_response(self.parent_r)
                        if response == 'forward':

                            try:
                                Relay_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                Relay_socket.connect((destination_host,80))
                            except socket.error,IOError:
                                pdb.set_trace()
                                if Relay_socket:
                                    Relay_socket.close()
                                message = "status: error opening relay socket"
                                msglen = msg_len(message)
                                os.write(child_w, msglen + message)
                                break
                            except socket.gaierror:
                                pdb.set_trace()
                                if Relay_socket:
                                    Relay_socket.close()
                                message = "status: gaierror!!!!"
                                msglen = msg_len(message)
                                os.write(child_w, msglen + message)
                                break

                            Relay_socket.sendall(HTTP_Request)
                            message = 'status: Forwarding to host'
                            msglen = msg_len(message)
                            os.write(self.child_w, msglen + message)
                            try:
                                Relay_socket.settimeout(5)
                                HTTP_Response = ""

                                while True:
                                    try:
                                        Line = Relay_socket.recv(self.max)
                                        if Line != "":
                                            HTTP_Response += Line
                                        else:
                                            break
                                    except socket.timeout, socket.error:
                                        #message = 'status: timeout or socket error'
                                        #msglen = msg_len(message)
                                        #os.write(self.child_w, msglen + message)
                                        break
                                    except IOError:
                                        message = 'status: ioerror'
                                        msglen = msg_len(message)
                                        os.write(self.child_w, msglen + message)
                                        break

                            finally:
                                if not HTTP_Response == "":
                                    message = 'data:' + HTTP_Response
                                    msglen = msg_len(message)
                                    os.write(self.child_w, msglen + message)
                                    response_action = check_for_response(self.parent_r)
                                    if response_action == 'forward':
                                        message = 'status: Forwarding to browser'
                                        msglen = msg_len(message)
                                        os.write(self.child_w, msglen + message)
                                        self.client.sendall(HTTP_Response)
                                    else:
                                        pass
                                else:
                                    pass
                            Relay_socket.close()
                        else:
                            pass
        self.client.close()
        isAvailable = True

if __name__ == '__main__':
    s = Server()
    s.run()
