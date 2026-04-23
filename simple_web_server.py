########################################################
# SimpleWebServer.py
# This toy web server is used to illustrate security
# vulnerabilities. This web server only supports
# extremely simple HTTP GET requests.
########################################################

import socket
import os
import io
from datetime import datetime


class SimpleWebServer:

    # Run the HTTP server on this TCP port.
    PORT = 8080

    # Question 3
    MAX_FILE_SIZE = 50 * 1024

    # The socket used to process incoming connections from web clients
    dServerSocket = None

    def __init__(self):
        SimpleWebServer.dServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        SimpleWebServer.dServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        SimpleWebServer.dServerSocket.bind(('', self.PORT))
        SimpleWebServer.dServerSocket.listen()

    def run(self):
        while True:
            # wait for a connection from a client
            s, addr = SimpleWebServer.dServerSocket.accept()

            # then process the client's request
            self.processRequest(s)

    # Reads the HTTP request from the client, and responds with the file
    # the user requested or a HTTP error code.
    def processRequest(self, s):
        # used to read data from the client
        br = io.TextIOWrapper(s.makefile('rb'), newline='\n')

        # used to write data to the client
        osw = io.TextIOWrapper(s.makefile('wb'), newline='', write_through=True)

        # read the HTTP request from the client
        request = br.readline().rstrip('\n')
        print(request)

        command = None
        pathname = None

        # parse the HTTP request
        st = None
        try:
            st = request.split()
            if len(st) == 0:
                raise ValueError("null request")
        except Exception:
            return

        command = st[0]
        pathname = st[1]

        self.logEntry("log.txt", command + " " + pathname)

        if command == "GET":
            # if the request is a GET try to respond with the file the user is requesting
            print("Path name: " + pathname)
            self.serveFile(osw, pathname)

        elif command == "PUT":
            print("Path name: " + pathname)
            self.storeFile(br, osw, pathname)

        else:
            # if the request is NOT a GET, return an error saying this server
            # does not implement the requested command
            osw.write("HTTP/1.0 501 Not Implemented\n\n")

        # close the connection to the client
        try:
            osw.close()
        except Exception:
            pass

    # Question 3
    def serveFile(self, osw, pathname):
        fr = None
        c = -1
        sb = ""

        # remove the initial slash at the beginning of the pathname in the request
        if pathname[0] == '/':
            pathname = pathname[1:]

        # if there was no filename specified by the client, serve the "index.html" file
        if pathname == "":
            pathname = "index.html"

        # Question 3
        f_size = os.path.getsize(pathname) if os.path.exists(pathname) else 0
        print(f_size)
        if f_size > self.MAX_FILE_SIZE:
            self.logEntry("error_log.txt", pathname + " exceeds max size limit: " + str(self.MAX_FILE_SIZE) + "\n")
            osw.write("HTTP/1.0 403 Forbidden\n\n")
            return

        # try to open file specified by pathname
        try:
            # System.out.println("Path name: "+pathname)
            fr = open(pathname, 'r')
            c = fr.read(1)
            c = ord(c) if c else -1
        except Exception:
            # if the file is not found, return the appropriate HTTP response code
            osw.write("HTTP/1.0 404 Not Found\n\n")
            return

        # if the requested file can be successfully opened
        # and read, then return an OK response code and
        # send the contents of the file
        osw.write("HTTP/1.0 200 OK\n\n")
        while c != -1:
            sb += chr(c)
            ch = fr.read(1)
            c = ord(ch) if ch else -1
        osw.write(sb)

    # Question 2
    def storeFile(self, br, osw, pathname):
        fw = None
        sc = br  # Scanner(br) — br is already a line-readable stream
        try:
            fw = open(pathname, 'w')
            s = sc.readline().rstrip('\n')
            while s is not None and s != "":
                fw.write(s + "\n")
                s = sc.readline().rstrip('\n')
            fw.close()
            osw.write("HTP/1.0 201 Created")   # bug preserved from original
            print(pathname + " is saved!")
        except Exception:
            osw.write("HTTP/1.0 500 Internal Server Error")
        print("storeFile is done!")

    # Question 2
    def logEntry(self, filename, record):
        fw = open(filename, 'a')
        fw.write(str(datetime.now()) + " " + record + "\n")
        fw.close()

    # This method is called when the program is run from the command line.
    @staticmethod
    def main():
        # Create a SimpleWebServer object, and run it
        sws = SimpleWebServer()
        sws.run()


if __name__ == '__main__':
    SimpleWebServer.main()