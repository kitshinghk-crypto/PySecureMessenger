#!/usr/bin/python3
from nacl.public import PrivateKey, Box, PublicKey
import requests
from random import randint
from base64 import b64encode, b64decode
from threading import Thread
import time
import curses
from curses import wrapper
import urllib3
urllib3.disable_warnings(urllib3.exceptions.SubjectAltNameWarning)

server_endpoint="https://localhost:4443"
sk = PrivateKey.generate()
pk = sk.public_key
user_id = -1
isLineBreak=False

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

def init_id():
    global user_id 
    user_id = str(random_with_N_digits(5))
    user_info = {"id":user_id, "pk":b64encode(pk.__bytes__()).decode("ascii")}
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
    msg_payload={"sender_id":sender_id, "recipient_id": recipient_id, "msg": msg}
    response=requests.post(server_endpoint+"/sendMsg", json=msg_payload, verify='cert.pem')
    if response.text == "Fail":
        print("[MESSAGE CANNOT BE SENT]")

def get_msg(my_id, from_id):
    getMsg_payload={"id": my_id, "from":from_id}
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
                if isLineBreak:
                    print(" ")
                print("<"+decrypted_msg)
        time.sleep(5)

def main():
    global user_id
    recipent=init_conversation()
    recipent_id = recipent["id"]
    recipent_pk = PublicKey(b64decode(recipent["pk"]))
    mybox = Box(sk, recipent_pk)
    t = Thread(target=print_msg, args=(user_id, recipent_id, mybox,))
    t.start()
    while True:
        isLineBreak=True
        message = input("msg>")
        isLineBreak=False
        if message:
            encrypted_message = mybox.encrypt(message.encode("utf-8"))
            encoded_message = b64encode(encrypted_message).decode("ascii")
            send_msg(user_id, recipent_id, encoded_message)

if __name__ == '__main__':
    main()