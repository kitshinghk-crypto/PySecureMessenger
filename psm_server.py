#!/usr/bin/python3
from http.server import HTTPServer
from PsmHTTPRequestHandler import PsmHTTPRequestHandler
import ssl

httpd = HTTPServer(('localhost', 4443), PsmHTTPRequestHandler)

httpd.socket = ssl.wrap_socket (httpd.socket, 
        keyfile="key.pem", 
        certfile='cert.pem', server_side=True)

httpd.serve_forever()