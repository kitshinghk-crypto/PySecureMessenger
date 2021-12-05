#!/usr/bin/python3
from http.server import HTTPServer
from PsmHTTPRequestHandler import PsmHTTPRequestHandler
import ssl
import time
from threading import Thread

def cleanIdleUser():
    while True:
        time.sleep(60)
        print("Start clean Idle users")
        for user_id in list(PsmHTTPRequestHandler.users.keys()):
            if time.time() - PsmHTTPRequestHandler.users[user_id]["lastActivity"] > 600:
                print(f"Clean idle user: user_id={user_id}")
                del PsmHTTPRequestHandler.users[user_id]
                del PsmHTTPRequestHandler.mailbox[user_id]

t=Thread(target=cleanIdleUser)
t.start()
httpd = HTTPServer(('localhost', 4443), PsmHTTPRequestHandler)
httpd.socket = ssl.wrap_socket (httpd.socket, 
        keyfile="key.pem", 
        certfile='cert.pem', server_side=True)
httpd.serve_forever()
