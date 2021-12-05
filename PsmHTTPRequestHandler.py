from http.server import BaseHTTPRequestHandler
from nacl.signing import SigningKey, VerifyKey
from nacl.encoding import Base64Encoder
from time import time
import struct
from random import randint
import json

class PsmHTTPRequestHandler(BaseHTTPRequestHandler):
    users={}
    mailbox={}
    
    def do_GET(self):
        if self.path == '/alive':
            self.do_alive()
        
    def do_POST(self):
        if self.path =='/getRecipientPk':
            self.do_getRecipientPk()
        elif self.path == '/start':
            self.do_start()
        elif self.path == '/sendMsg':
            self.do_sendMsg()
        elif self.path == '/getMsg':
            self.do_getMsg()

    def do_alive(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("alive", "utf-8"))

    # POST /getMsg
    # param: {"id":"123", "from":"456", "sign":"signature"}
    def do_getMsg(self):
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        getMsg_info = json.loads(post_body.decode('utf-8'))
        user_id = getMsg_info["id"]
        from_id = getMsg_info["from"]
        signature = getMsg_info["sign"]
        verify_key = VerifyKey(self.users[user_id]["vk"].encode("ascii"), encoder=Base64Encoder)
        verify_msg = verify_key.verify(signature.encode("ascii"), encoder=Base64Encoder)
        sign_time = struct.unpack(">i", verify_msg)[0]
        if time()-sign_time>30:
            print(f"SIGNATURE EXPIRED: user={user_id}")
            return
        self.users[user_id]["lastActivity"] = time()
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        if user_id in self.users and user_id in self.mailbox and from_id in self.mailbox[user_id]:
            msgs = {"msgs": self.mailbox[user_id][from_id]}
            self.mailbox[user_id][from_id] = []
            self.wfile.write(json.dumps(msgs).encode('utf-8'))
        else:
            self.wfile.write(bytes("Fail", "utf-8"))


    # POST /sendMsg
    # param: {"sender_id":"123", "recipient_id":"456", "msg":"encrypted message", "sign":"signature"}
    def do_sendMsg(self):
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        msg_info = json.loads(post_body.decode('utf-8'))
        sender_id = str(msg_info["sender_id"])
        recipient_id = str(msg_info["recipient_id"])
        encrypted_msg = msg_info["msg"]
        signature = msg_info["sign"]
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        if sender_id in self.users and recipient_id in self.users and sender_id!=recipient_id:
            verify_key = VerifyKey(self.users[sender_id]["vk"].encode("ascii"), encoder=Base64Encoder)
            verify_msg = verify_key.verify(signature.encode("ascii"), encoder=Base64Encoder)
            sign_time = struct.unpack(">i", verify_msg)[0]
            if time()-sign_time>30:
                print(f"SIGNATURE EXPIRED: user={sender_id}")
                return
            if recipient_id not in self.mailbox:
                self.mailbox[recipient_id]={}
            if sender_id not in self.mailbox[recipient_id]:
                self.mailbox[recipient_id][sender_id] = []
            self.mailbox[recipient_id][sender_id].append(encrypted_msg)
            self.wfile.write(bytes("ok", "utf-8"))
        else:
            self.wfile.write(bytes("Fail", "utf-8"))

    # POST /getRecipientPk
    # param: {"id":"12345"}
    def do_getRecipientPk(self):
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        user_info = json.loads(post_body.decode('utf-8'))
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        if user_info["id"] in self.users:
            self.wfile.write(json.dumps(self.users[user_info["id"]]).encode('utf-8'))
        else:
            self.wfile.write(bytes("Fail", "utf-8"))

    # POST /start
    # param: {"id": "12345", "pk":"public_key"}
    def do_start(self):
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        user_info = json.loads(post_body.decode('utf-8'))
        user_info["lastActivity"]=time()
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        if user_info["id"] in self.users:
            self.wfile.write(bytes("Fail", "utf-8"))
        else:
            self.users[str(user_info["id"])]=user_info
            self.mailbox[str(user_info["id"])]={}
            self.wfile.write(bytes("ok", "utf-8"))
        
        
        
    


        
