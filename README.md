# PySecureMessenger
A python secure messenger developed using pynacl. The messenger consists of the server module and the client module. A certificate and key files should be provided to the server scirpt for TLS support. The messengers uses end-to-end encryption, which means the plaintext message is encrypted and the ciphertext message is decrypted in the client side. The client use pynacl Curve25519 for public key encryption and Ed25519 for authenication. The server does not store messages in plaintext. Once the messages in the mailbox is deliveried to the client, the messenges in the server are removed. 

## Server
The server side has 2 purposes:
1. As a KDC which stores and distributes the public key of the users. 
2. As a mailbox which stores all encrypted messages for each users. 

It provides REST API service for the messenger client to send/receive messages. With certificate and key provided, the server supports TLS.

## Client
Run the client script, and it will return the following:
```
Your ID: 12077
Enter your recipient ID:
```
The client return a one-time user id to the users when the client program starts. The public and private keys pair is generated on the fly and is only used in a converation. The keys are stored in the program memory. Give the ID to the recipient and start the conversation.

<span>
<img src="https://github.com/kitshinghk-crypto/PySecureMessenger/blob/master/psm_screenshot.png?raw=true" alt="Your image title" width="300"/>
<img src="https://github.com/kitshinghk-crypto/PySecureMessenger/blob/master/psm_screenshot_2.png?raw=true" alt="Your image title" width="300"/>
</span>
