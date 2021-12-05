#!/usr/bin/python3
from nacl.public import PrivateKey, Box, PublicKey
from nacl.signing import SigningKey, VerifyKey
from nacl.encoding import Base64Encoder
import requests
from random import randint
from base64 import b64encode, b64decode
from threading import Thread
import time
import curses
from curses import wrapper
import urllib3
import struct
import json
urllib3.disable_warnings(urllib3.exceptions.SubjectAltNameWarning)

server_endpoint="https://localhost:4443"
signKey = SigningKey.generate()
vk = signKey.verify_key
sk = signKey.to_curve25519_private_key()
pk = vk.to_curve25519_public_key()
user_id = -1
isLineBreak=False
offsetY=2
offsetX=3
chatUiWidth=60
chatUiHeight=40
maxMsgLen=chatUiWidth-10

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

def init_id():
    global user_id 
    user_id = str(random_with_N_digits(5))
    user_info = {"id":user_id, "pk":b64encode(pk.__bytes__()).decode("ascii"), "vk": b64encode(vk.__bytes__()).decode("ascii")}
    response=requests.post(server_endpoint+"/start", json=user_info, verify='cert.pem')
    return response.text

def get_getRecipientPk(id):
    user_info = {"id":id}
    response=requests.post(server_endpoint+"/getRecipientPk", json=user_info, verify='cert.pem')
    if response.text == "Fail":
        return 
    recipent_info = response.json()
    return recipent_info["pk"]

def get_recipientId():
    recipent_pk = ""
    while not recipent_pk:
        recipient_id = input("Enter your recipient ID:")
        recipent_pk = get_getRecipientPk(recipient_id)
        if not recipent_pk:
            print("Recipient ID not found")
    return {"id":recipient_id, "pk":recipent_pk}

def init_conversation():
    init_result = init_id()
    while init_result != "ok":
        init_result = init_id()
    print(f"Your ID: {user_id}")
    return get_recipientId()

def send_msg(sender_id, recipient_id, msg):
    msg_payload={"sender_id":sender_id, "recipient_id": recipient_id, "msg": msg, "sign": signKey.sign(struct.pack(">i", int(time.time())), encoder=Base64Encoder).decode("ascii")}
    response=requests.post(server_endpoint+"/sendMsg", json=msg_payload, verify='cert.pem')
    if response.text == "Fail":
        print("[MESSAGE CANNOT BE SENT]")
        return False
    return True

def get_msg(my_id, from_id):
    getMsg_payload={"id": my_id, "from":from_id, "sign": signKey.sign(struct.pack(">i", int(time.time())), encoder=Base64Encoder).decode("ascii")}
    response=requests.post(server_endpoint+"/getMsg", json=getMsg_payload, verify='cert.pem')
    if response.text == "Fail":
        return
    return response.json()

def print_msg(my_id, from_id, box):
    while True:
        msgs = get_msg(my_id,from_id)
        if msgs:
            for msg in msgs["msgs"]:
                decoded_msg = b64decode(msg)
                decrypted_msg = box.decrypt(decoded_msg).decode('utf-8')
                print("<"+decrypted_msg)
        time.sleep(5)

def chat_render(chatbox, my_id, from_id, box):
    global offsetX, offsetY
    while True:
        msgs = get_msg(my_id,from_id)
        if msgs:
            for msg in msgs["msgs"]:
                decoded_msg = b64decode(msg)
                decrypted_msg = box.decrypt(decoded_msg).decode('utf-8')
                chatbox.addstr(offsetY,offsetX,"<"+decrypted_msg,curses.color_pair(2))
                offsetY+=1
                chatbox.refresh(max(0,offsetY-chatUiHeight),0, 0,0, chatUiHeight, chatUiWidth)
        time.sleep(5)

def chat_main(stdscr,mybox,recipent_id):
    global offsetX, offsetY
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    chatbox = curses.newpad(1000, chatUiWidth)
    chatbox.box()
    chatbox.refresh(0,0,0,0,chatUiHeight, chatUiWidth)
    t = Thread(target=chat_render, args=(chatbox, user_id, recipent_id, mybox,))
    t.start()
    curses.echo()
    while True:
        textbox = curses.newwin(5, chatUiWidth, 42, 0)
        textbox.box()
        textbox.addstr(2,5,"msg>")
        textbox.addstr(3,5,"Your ID: "+user_id +" Recipent ID:"+recipent_id)
        textbox.refresh()
        message = textbox.getstr(2,10,maxMsgLen)
        if message:
            encrypted_message = mybox.encrypt(message)
            encoded_message = b64encode(encrypted_message).decode("ascii")
            if send_msg(user_id, recipent_id, encoded_message):
                chatbox.addstr(offsetY,offsetX,b">"+message,curses.color_pair(1))
                offsetY+=1
                chatbox.refresh(max(0,offsetY-chatUiHeight),0, 0,0, chatUiHeight, chatUiWidth)

def main():
    global user_id
    recipent=init_conversation()
    recipent_id = recipent["id"]
    recipent_pk = PublicKey(b64decode(recipent["pk"]))
    mybox = Box(sk, recipent_pk)
    wrapper(chat_main,mybox,recipent_id)
    #t = Thread(target=print_msg, args=(user_id, recipent_id, mybox,))
    #t.start()

if __name__ == '__main__':
    main()