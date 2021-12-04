# PySecureMessenger
A python secure messenger developed using pynacl. The messenger consists of the server module and the client module. A certificate and key files should be provided to the server scirpt for TLS support. The messengers support end-to-end encryption, which means the plaintext message is encrypted and the encrypted ciphertext message is decrypted in the client side. The server does not store the private key of the users or messages in plaintext. 

## Server
The server side has 2 purposes:
1. As a KDC which stores the public of the users. 
2. As a mailbox which stores all encrypted messages for each users. 

It provides REST API service for the messenger client to send/receive messages. With certificate and key provided, the server supports TLS.

## Client
Run the client script, and it will return the following:
```
Your ID: 12077
Enter your recipient ID:
```
The client return a one-time user id to the users when the client program starts. Give the ID to the intented recipient and start the conversation.

<span>
<img src="https://github.com/kitshinghk-crypto/PySecureMessenger/blob/master/psm_screenshot.png?raw=true" alt="Your image title" width="300"/>
<img src="https://github.com/kitshinghk-crypto/PySecureMessenger/blob/master/psm_screenshot_2.png?raw=true" alt="Your image title" width="300"/>
</span>
