import socket, sys, pdb
import threading
import Queue

# Importing HTTP_PARSER to get destination host from HTTP Request
# try to import C parser then fallback in pure python parser.
try:
    from http_parser.parser import HttpParser
except ImportError:
    from http_parser.pyparser import HttpParser



class Server:
    def __init__(self):
        queue = Queue.Queue()
        self.threads = []
        self.localhost = '0.0.0.0'
        self.port = 8080
        self.max = 999999
        self.q = queue

    def open_socket(self):
        try:
            self.Listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.Listener_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.Listener_socket.bind((self.localhost, self.port))
            self.Listener_socket.listen(5)
            #status = 'Listening at ', self.Listener_socket.getsockname()
            #return status

        except socket.error, (value, message):
            if self.Listener_socket:
                self.Listener_socket.close()
            sys.exit(1)

    def run(self):
        self.open_socket()
        while True:
            c = Client(self.Listener_socket.accept(), self.q)
            c.start()
            self.threads.append(c)
        # close all threads
        self.Listener_socket.close()
        for c in self.threads:
            c.join()

class Client(threading.Thread):

    def __init__(self,(client, address), q):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.max = 999999
        self.q = q

    def run(self):

        HTTP_Request = self.client.recv(self.max)
        p = HttpParser()
        header_done = False
        destination_host = ''

        if HTTP_Request:
            print 'Got something from ' + str(self.address) + '...'
            request_length = len(HTTP_Request)
            nparsed = p.execute(HTTP_Request, request_length)
            assert nparsed == request_length

            if p.is_headers_complete() and not header_done:
                print(p.get_headers())
                print(p.get_headers()['Host'])
                destination_host = p.get_headers()['Host']
                header_done = True

                ''' Ready to process send but need to display HTTP_Request in UI first
                  and wait for forward.

                  - Add HTTP_Request to queue'''
                self.q.put(HTTP_Request)
                Relay_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                Relay_socket.connect((destination_host,80))
                Relay_socket.sendall(HTTP_Request)
                print 'Forwarding data to destination host...'

                while True:
                    HTTP_Response = Relay_socket.recv(self.max)
                    if not HTTP_Response:
                        break
                    else:
                        print 'Received data back. Forwarding to the client...'
                        self.client.sendall(HTTP_Response)

            self.client.close()
            Relay_socket.close()

if __name__ == '__main__':
    s = Server()
    s.run()