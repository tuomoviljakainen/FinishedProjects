import socket
import ssl
import sys
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from termcolor import colored
import threading
import hashlib
import getpass
import os
import time

# Contains username
active_client = None
# Holds private and public keys before writing them to files
private_key = None
public_key = None

welcome = ("""

 #######  ##    ## ##       #### ##    ## ########
##     ## ###   ## ##        ##  ###   ## ##
##     ## ####  ## ##        ##  ####  ## ##
##     ## ## ## ## ##        ##  ## ## ## ######
##     ## ##  #### ##        ##  ##  #### ##
##     ## ##   ### ##        ##  ##   ### ##
 #######  ##    ## ######## #### ##    ## ########

Welcome to the chat server! You can send messages by typing them and pressing enter!

To exit the program, type "exit()"

""")

# Used to define username for login
def setUsername():
    while True:
        print("Give username: " , end="")
        username = input()
        if not username:
            print(colored("Username cannot be empty", "red"))
            continue
        else:
            return username

# Used to set password for login
def setPassword():
    while True:
        password = getpass.getpass()
        if len(password) < 8:
            print(colored("Password is not valid length, minimum length is 8 characters!", "red"))
            continue
        else:
            return password

# Used to set IP address for login
def setIPAddress():
    while True:
        print("Give IP address: ", end="")
        address = input()
        if not address:
            print(colored("Address cannot be empty","red"))
        else:
            return address

# Used to set port for login
def setPort():
    while True:
        print("Give Port: ", end="")
        port = input()
        if str(port).isdigit() and not None:
            return int(port)
        else:
            print(colored("Give valid port!", "red"))

# Asks client for credentials in setUsername and setPassword functions and passes all required information needed for chat login to connect function
def credentials(method, address, port):

    while True:
        username = setUsername()
        password = setPassword()

        if not username or not password:
            print(colored("Username or password cannot be empty!", "red"))
        else:
            connect(method, username, password, address, port)
            return

# User interface where client can choose either to register/login or change server's IP address or port
def userInterface():

    with open("client.conf", "r") as confFile:
        info = confFile.read()
        address = info.split(":")[0]
        port = int(info.split(":")[1])

    while True:
        print(colored("Server: %s" % address,"green"))
        print(colored("Port: %s" % port, "green"))

        print("""
        Options:
        1. Register
        2. Login
        3. Change server info

        To exit the program, type "exit()"

        """)

        while True:
            option = input()
            if option not in("1", "2", "3", "exit()"):
                print("Give valid option!")
                continue
            else:
                break

        if option == "1":
            credentials("register", address, port)
        elif option == "2":
            credentials("login", address, port)
        elif option == "3":
            address = setIPAddress()
            port = setPort()
            with open("client.conf", "w") as confFile:
                confFile.write(address + ":" + str(port))
        elif option == "exit()":
            print("Exiting program... ")
            time.sleep(2)
            sys.exit(0)
        else:
            print("Unable to proceed!")
            sys.exit()

# Private and public keys are created for user when registering
def createKeys(username):

    global private_key
    global public_key
    # If private/public key pair already exist for username, we save them to global variable
    if os.path.exists("keymanagement/clients/" + username + "-private.pem") and os.path.exists("keymanagement/clients/" + username + "-public.pem"):
        with open("keymanagement/clients/" + username + "-private.pem", "r") as keyFile:
            clientKey = keyFile.read()
            private_key = clientKey
        with open("keymanagement/clients/" + username + "-public.pem", "r") as keyFile:
            clientKey = keyFile.read()
            public_key = clientKey.encode()
    # New public/private key pairs are created if they do not already exist
    else:
        private_key = RSA.generate(1024)
        public_key = private_key.publickey()
        private_key = private_key.exportKey("PEM")
        public_key = public_key.exportKey("OpenSSH")

# Private/public key pairs are written to files
def writeKeys(username):
    global private_key
    f = open("keymanagement/clients/" + username + "-private.pem", "wb")
    try:
        f.write(private_key.encode())
    except AttributeError:
        f.write(private_key)
    f.close()

    global public_key
    f = open("keymanagement/clients/" + username + "-public.pem", "wb")
    f.write(public_key)
    f.close()

# Writing public key server send, into a file when registering
def keyRegister(public):
    with open("keymanagement/servers/server-public.pem", "w+") as keyFile:
        keyFile.write(public)

# Returns message that client sends to server when registering
def registerMessage(username, password):
    # Putting publickey, username and password to server
    global public_key
    message = Base64EncodeMessage("REG." + username + "." + password + "." + public_key.decode())
    return message

# Returns message that client sends to server when logging in
def loginMessage(username, password):
    message = Base64EncodeMessage("LOG." + username + "." + password)
    return message

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

# Contains functionality to send chat messages to server
def sendMessage(ssock, cookie):

    os.system("clear")
    print(welcome)
    # Loop that sends chat messages to server when client presses Enter
    sys.stdout.write("\033[34m"+'\n[Me :] '+ "\033[0m"); sys.stdout.flush()
    while True:
        msg = sys.stdin.readline()
        if msg == "exit()\n":
            print("Exiting program...")
            time.sleep(2)
            sys.exit(0)
        else:
            rimpsu = Base64EncodeMessage("MSG." + cookie + "." + msg)
            # Encrypting chat message with servers public key before sending
            encryptedReply = encryptMessage(rimpsu)
            try:
                ssock.sendall(base64.b64encode(encryptedReply) + "\r\n\r\n".encode())
            except:
                return
                #print("The server is not responding, exiting...")
                #time.sleep(2)
                #sys.exit(0)
            #sys.stdout.write("\033[34m"+'\n[Me :] '+ "\033[0m"); sys.stdout.flush()

# Encrypts message with servers public key
def encryptMessage(message):
    with open("keymanagement/servers/server-public.pem", "r") as keyFile:
        pubKey = keyFile.read()
        imported = RSA.importKey(pubKey)
        cipher = PKCS1_OAEP.new(imported)
        encryptedReply = cipher.encrypt(message)
        return encryptedReply

# Decrypting message with clients private key
def DecryptMessage(message):
    message = message.split("\r\n\r\n")[0]
    message = base64.b64decode(message.encode())
    with open("keymanagement/clients/" + active_client + "-private.pem", "r") as keyFile:
        clientKey = keyFile.read()
        imported = RSA.importKey(clientKey)
        cipher = PKCS1_OAEP.new(imported)
        decryptedMessage = cipher.decrypt(message)
        return decryptedMessage

# Contains functionality to receive chat messages from server
def receiveMessage(ssock):
    response = b""
    data = b""
    message = ""
    # Looping while connection to chat server is up
    while True:
        # Listens data from server
        while "\r\n\r\n" not in response.decode("utf-8"):
            data = ssock.recv(4096)
            response += data
            # If connection dies
            if not data:
                print(colored("The server has closed the connection for an unknown reason", "red"))
                sys.exit(0)
                sys.exit(0)
        response = response.decode()
        if active_client:
            message = response.split("\r\n\r\n")[0]
            # Decrypting message received from server with clients private key
            decryptedMessage = DecryptMessage(message)
            #print(decryptedMessage)
            message = Base64DecodeMessage(decryptedMessage.decode()).decode()
            #print(message)
            # If method is MSG, another user has sent message and it gets printed
            if message.split(".")[0] == "MSG":
                sys.stdout.write("\r" + "[" + message.split(".")[1] + "] " + message.split(".")[2])
            elif message.split(".")[0] == "OK" and message.split(".")[1] == "103":
                userLogin = processResponse(Base64EncodeMessage(message), ssock, active_client)
                sys.stdout.write(colored("\r" + "[" + userLogin + "] " + "has joined the server!","green"))
            elif message.split(".")[0] == "OK":
                processResponse(Base64EncodeMessage(message), ssock, active_client)
            elif message.split(".")[0] == "ERR":
                processResponse(Base64EncodeMessage(message), ssock, active_client)
        sys.stdout.write("\033[34m"+'\n[Me :] '+ "\033[0m"); sys.stdout.flush()
        response = b""
        data = b""

# Contains functionality to process messages received from server
def processResponse(response, ssock, username):
    response = response.decode("utf-8")
    cookie = ""
    # If response is 102, method, responsecode, cookie and servers publickey are saved to variables and public key is written to file
    if base64.b64decode(response.split(".")[1]).decode("utf-8") == "102":
        responseMethod = base64.b64decode(response.split(".")[0]).decode("utf-8")
        responseCode = base64.b64decode(response.split(".")[1]).decode("utf-8")
        cookie = base64.b64decode(response.split(".")[2]).decode("utf-8")
        srvPubKey = base64.b64decode(response.split(".")[3].split("\r\n\r\n")[0]).decode("utf-8")
        keyRegister(srvPubKey)
    # If response code is 103, method, responsecode and username are saved to variables
    elif Base64DecodeMessage(response.split(".")[1]).decode() == "103":
        response = Base64DecodeMessage(response).decode()
        responseMethod = response.split(".")[0]
        responseCode = response.split(".")[1]
        responseUser = response.split(".")[2].split("\r\n\r\n")[0]
    # In other cases responsemethod and responsecode are put into variables
    else:
        responseMethod = base64.b64decode(response.split(".")[0]).decode("utf-8")
        responseCode = base64.b64decode(response.split(".")[1].split("\r\n\r\n")[0]).decode("utf-8")

    # If method is ERR, error message is printed to user depending on error code
    if responseMethod == "ERR":
        if responseCode == "201":
            print(colored("Error! Username already exists", "red"))
        elif responseCode == "301":
            print(colored("Incorrect username", "red"))
        elif responseCode == "302":
            print(colored("Incorrect password", "red"))
        elif responseCode == "401":
            print(colored("Message could not be sent to some or all users", "red"))
        ssock.close()
        return
    # If method is OK
    elif responseMethod == "OK":
        # User has been successfully created in server side
        if responseCode == "101":
            print(colored("User was succesfully created!", "green"))
            writeKeys(username)
            return
        # User has successfully logged in, functionality to send and receive messages are set up
        elif responseCode == "102":
            global active_client
            active_client = username
            print("Client name: %s" % active_client)
            threading.Thread(target=receiveMessage, args=(ssock,)).start()
            sendMessage(ssock, cookie)
            return
        # Another user has joined server, username is returned
        elif responseCode == "103":
            return responseUser
        elif responseCode == "104":
            return
    return

# Used to establish connection to server
def connect(method, username, password, address, port):
    # private/public keys are created for user and register message is created
    if method == "register":
        createKeys(username)
        message = registerMessage(username, password)
    # Login message is created
    elif method == "login":
        message = loginMessage(username, password)

    hostname = "chatserver"
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations("../cert/ca.cer")
    # Secure connection to server gets established
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            try:
                ssock.connect((address, port))
                # Message is send to server
                ssock.send(message + "\r\n\r\n".encode("utf-8"))
                response = b""
            except:
                print(colored("Connection refused by the server", "red"))
                return
            while "\r\n\r\n" not in response.decode("utf-8"):
                data = ssock.recv(4096)
                response += data
            # Processing response received from server
            processResponse(response, ssock, username)
            return

if __name__ == "__main__":
    # Starting UI
    userInterface()
