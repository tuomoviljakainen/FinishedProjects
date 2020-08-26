import socket
import sys
import os
import binascii
import ssl
import threading
import base64
import hashlib
import secrets
import string
from termcolor import colored
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from datetime import datetime
#import ConfigParser

# Contains logged in clients inside a list and each connection inside tuple that contains username, socket and cookie
active_clients = []

# Used to lock files and objects, so that only one user can modify/read files or object at a time, preventing mixups.
secret_file_lock = threading.Lock()
active_client_lock = threading.Lock()
server_key_lock = threading.Lock()

# Used to process client's registration attempt
def registerUser(username, password, pubkey, addr, client):
    # If password is too short or too long, error message is returned to client
    if len(password) < 8 or len(password) > 32:
        print("<" + colored(datetime.now().strftime("%H:%M:%S"), "blue") + "> " + "Password is not valid length")
        return Base64EncodeMessage("ERR.202")

    # If username already exists in secret.txt, error is returned to the client
    secret_file_lock.acquire()
    with open("users/secret.txt", "r+") as userfile:
        for line in userfile:
            if line.split(".")[0] == username:
                print("<" + colored(datetime.now().strftime("%H:%M:%S"), "blue") + "> ", colored("Failed to register user {1} because it already exists {0}".format(addr, base64.b64decode(username.encode()).decode()), "red"))
                secret_file_lock.release()
                return Base64EncodeMessage("ERR.201")
    secret_file_lock.release()

    # Base64 encoded SHA-256 hash is created from the password that user gave
    base64passwordhash = base64.b64encode(hashlib.sha256(password).hexdigest().encode("utf-8"))

    # If there are no issues in the registration; username, hashed password and public key will be base64 encoded and added to secret.txt
    secret_file_lock.acquire()
    with open("users/secret.txt", "a+", newline="") as userfile:
        userfile.write(username + "." + base64passwordhash.decode("utf-8") + "." + pubkey)
        print("<" + colored(datetime.now().strftime("%H:%M:%S"), "blue") + "> ", colored("User {0} registered succesfully from {1}".format(base64.b64decode(username.encode()).decode(), addr),"magenta"))
        secret_file_lock.release()
        return Base64EncodeMessage("OK.101")
    secret_file_lock.release()
    return

# Used to process client's logging in attempt
def loginUser(username, password, addr):
    # Hash is calculated from clients password and base64 encoded
    base64passwordhash = base64.b64encode(hashlib.sha256(password).hexdigest().encode("utf-8"))
    # If username is already in use, error message is returned
    active_client_lock.acquire()
    for connection in active_clients:
        if connection[1] == username:
            print("<" + colored(datetime.now().strftime("%H:%M:%S"), "blue") + "> ", colored("User " + username.decode() + " has already logged in","red"))
            active_client_lock.release()
            return Base64EncodeMessage("ERR.303")
    active_client_lock.release()

    secret_file_lock.acquire()
    with open("users/secret.txt", "r+") as userfile:
        for line in userfile:
            if base64.b64decode(line.split(".")[0]) == username:
                # If password's hash equals to the one in secret.txt, user can log in
                if line.split(".")[1] == base64passwordhash.decode("utf-8"):
                    print("<" + colored(datetime.now().strftime("%H:%M:%S"), "blue") + "> ", colored("User {0} logged in from {1}".format(username.decode(), addr), "green"))
                    secret_file_lock.release()
                    return Base64EncodeMessage("OK.102")
                # If password's hash doesn't equal to the one in secret.txt, error message is returned
                else:
                    print("<" + colored(datetime.now().strftime("%H:%M:%S"), "blue") + "> ", colored("Wrong password for user {0} from {1}".format(username.decode(), addr), "red"))
                    secret_file_lock.release()
                    return Base64EncodeMessage("ERR.302")
        # If username is not found from secret.txt, error message is returned
        print("<" + colored(datetime.now().strftime("%H:%M:%S"), "blue") + "> ",colored("Wrong username {0} from {1}".format(username.decode(), addr), "red"))
        secret_file_lock.release()
        return Base64EncodeMessage("ERR.301")

# Decrypting message with server's private key
def decryptMessage(message):
    message = message.decode()
    message = message.split("\r\n\r\n")[0]
    message = base64.b64decode(message.encode())
    server_key_lock.acquire()
    with open("server_keys/server-private.pem", "r") as keyFile:
        serverKey = keyFile.read()
        imported = RSA.importKey(serverKey)
        cipher = PKCS1_OAEP.new(imported)
        decryptedMessage = cipher.decrypt(message)
        server_key_lock.release()
        # Decrypted message is returned
        return decryptedMessage

# Encrypting message with clients public key
def encryptMessage(username, data):
    publicKey = ""
    secret_file_lock.acquire()
    with open("users/secret.txt", "r+") as userfile:
        for line in userfile:
            if base64.b64decode(line.split(".")[0]) == username:
                publicKey = RSA.importKey(base64.b64decode(line.split(".")[2]).decode())
                cipher = PKCS1_OAEP.new(publicKey)
                cipherText = cipher.encrypt(data)
                message = base64.b64encode(cipherText)
                secret_file_lock.release()
                # Returns base64 encoded encrypted message
                return message
    secret_file_lock.release()

# Contains functionality to process messages received from clients
def processMessage(client, message, addr):
    active_client_lock.acquire()
    # If connection is found from active_clients, it is decrypted
    for conn in active_clients:
        if conn[0] == client:
            message = decryptMessage(message)
    active_client_lock.release()
    parts = message.decode("utf-8").split(".")
    method = base64.b64decode(parts[0]).decode("utf-8")

    # If method is REG, client is trying to register and registerUser function is called
    if method == "REG":
        username = parts[1]
        password = base64.b64decode(parts[2])
        pubkey = parts[3]
        message = registerUser(username, password, pubkey, addr, client)
    # If method is LOG, client is trying to log in and loginUser function is called
    elif method == "LOG":
        username = base64.b64decode(parts[1])
        password = base64.b64decode(parts[2])
        message = loginUser(username,password,addr)

        # If connection is succesfull, add connection to list
        message = message.decode("utf-8")
        if Base64DecodeMessage(message) == "OK.102".encode("utf-8"):
            with open("server_keys/server-public.pem") as keyFile:
                publicKey = keyFile.read()
            # Create random cookie for the client
            cookie = "".join(secrets.choice(string.ascii_lowercase) for i in range(24))
            message = message.encode() + ".".encode() + Base64EncodeMessage(cookie + "." + publicKey)
            # Adding tuple to active client list that contains socket, username and cookie
            active_client_lock.acquire()
            # Add socket, username and cookie in tuple to active_clients list
            active_clients.append((client, username, cookie))
            # BroadcastMessage is called to tell all other logged in user's that this user logged in
            broadcastMessage(client, "OK", username, "103")
            active_client_lock.release()
        # If username or password is incorrect, return error message
        elif Base64DecodeMessage(message) == "ERR.302".encode("utf-8") or Base64DecodeMessage(message) == "ERR.301".encode("utf-8"):
            return message.encode()
    # If method is MSG, chat message was received
    elif method == "MSG":
        cookie = base64.b64decode(parts[1]).decode()
        active_client_lock.acquire()
        for client in active_clients:
            # If cookie is found from active_clients list
            if cookie == client[2]:
                username = client[1]
                message = parts[2].split("\r\n\r\n")[0]
                # Broadcast message to all other participants
                try:
                    broadcastMessage(client[0], "MSG", username, message)
                # In case of error, inform client that his message may not have been received by all participants
                except:
                    active_client_lock.release()
                    return encryptMessage(client[1], base64.b64encode("ERR.401".encode()))
                active_client_lock.release()
                # Tell client that his message was successfully send to all other clients in chat room
                return encryptMessage(client[1], base64.b64encode("OK.104".encode()))
        active_client_lock.release()
    else:
        return
    return message

# Listens messages from client
def Connection(client, addr):
    message = b""
    dc = False
    try:
        while True:
            # Receive data from client until CRLF
            while "\r\n\r\n" not in message.decode("utf-8"):
                try:
                    data = client.recv(4096)
                    message += data
                except:
                    continue
                # If connection is canceled by client, set dc to True
                if not data:
                    dc = True
                    break
        # Sending response to client
            if dc != True:
                # Sends client's message to be processed by processMessage that returns response
                response = processMessage(client, message, addr)
                # Send response to client
                try:
                    client.send(response + "\r\n\r\n".encode("utf-8"))
                except TypeError:
                    client.send(response.encode() + "\r\n\r\n".encode("utf-8"))
                message = b""
                data = ""
            else:
                break
    # If client disconnects, remove it from the active_clients list
    finally:
        disconnect(client)

# Encoding message parts with Base64
def Base64EncodeMessage(message):
    encodedMessage = b""
    parts = message.split(".")
    i = 1
    # Each part that is divided by dot, is separately base64 encoded
    for part in parts:
        if i == len(parts):
            encodedMessage += base64.b64encode(part.encode())
        else:
            encodedMessage += base64.b64encode(part.encode()) + ".".encode()
        i += 1
    # Encoded message is returned
    return encodedMessage

# Decoding message parts with Base64
def Base64DecodeMessage(message):
    decodedMessage = b""
    parts = message.split(".")
    i = 1
    # Each part that is divided by dot, is separately base64 decoded
    for part in parts:
        if i == len(parts):
            decodedMessage += base64.b64decode(part.encode())
        else:
            decodedMessage += base64.b64decode(part.encode()) + ".".encode()
        i += 1
    # Decoded message is returned
    return decodedMessage

# Removes client from active_clients list
def disconnect(connection):
    active_client_lock.acquire()
    for client in active_clients:
        if client[0] == connection:
            print("<" + colored(datetime.now().strftime("%H:%M:%S"), "blue") + "> ", colored("User {0} disconnected".format(client[1].decode()), "yellow"))
            active_clients.remove(client)
            active_client_lock.release()
            return
    active_client_lock.release()

# Broadcasts message to logged in clients, except the one who's socket is in connection parameter 
def broadcastMessage(connection, method, username, message):
    # If user joins the server
    if method == "OK" and message == "103":
        data = Base64EncodeMessage(method + "." + message + "." + username.decode())
    # If user sends chat message
    else:
        data = Base64EncodeMessage(method + "." + username.decode() + "." + base64.b64decode(message.encode()).decode())
        #print("<" + colored(datetime.now().strftime("%H:%M:%S"), "blue") + "> ", "User {0} send message: {1}".format(username.decode(), base64.b64decode(message.encode()).decode())
    for client in active_clients:
        # Sends message to all other clients
        if client[0] != connection:
            # Encrypt message with clients public key and send it
            try:
                encryptedMessage = encryptMessage(client[1], data)
                client[0].send(encryptedMessage + "\r\n\r\n".encode())
            # In case of error, close socket and remove client from active_clients list
            except:
                client[0].close()
                disconnect(client)

if __name__ == "__main__":
    # Sets up secure socket
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    server_key_lock.acquire()
    context.load_cert_chain('server_keys/server.cer', 'server_keys/server-private.pem')
    server_key_lock.release()
    # Start listening to the socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', 1337))
        sock.listen(5)
        # When new connection is established, create new thread for it that calls Connection method with socket and address as its parameters
        with context.wrap_socket(sock, server_side=True) as ssock:
            while True:
                conn, addr = ssock.accept()
                threading.Thread(target=Connection, args=(conn, addr)).start()
