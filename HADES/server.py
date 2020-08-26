# -*- coding: utf-8 -*-

import sys
import socket
import os
import binascii

VERSION = "1.0"
VALID_HADES_METHODS = ["DELETE", "UPLOAD", "LIST", "DOWNLOAD"]

# Used to define servers host address
def DefineAddress():
    HOST = input("Give new host: ")
    return HOST

# Used to define servers port
def DefinePort():
    PORT = input("Give new Port: ")
    return int(PORT)

# Used to define key and methods that require it 
def DefineKey():
    while 1:
        wrongMethod = 0
        addKey = input("Add key yes/no: ").lower()
        if addKey in ("y", "yes"):
            key = input("Give new Key: ")
            if not key:
                print("Give valid key!")
                continue
            print("Available methods:")
            for value in VALID_HADES_METHODS:
                print(value)
            methods = input("Which methods require a key (If you give several methods, separate them from each other with space): ")
            methods = methods.split(" ")
            for method in methods:
                if not method in VALID_HADES_METHODS:
                    print("Give valid values!")
                    wrongMethod = 1
                    break
            if wrongMethod:
                continue
            else:
                KEY={"key":key, "methods":methods}
                return KEY
        elif addKey in ("n", "no"):
            KEY={"key":None, "methods":None}
            return KEY
        else:
            print("Answer yes or no")
            continue

# Used to define supported hades versions that server supports
def DefineVersion():
    VERSIONS = input("Give supported protocol versions (If you give several, separate them from each other with space):")
    VERSIONS = VERSIONS.split()
    return VERSIONS

# User interface to change servers settings
def SetUpServer(HOST="localhost", PORT=1716, KEY={"key":None, "methods":None}, VERSIONS=["1.0"]):
    while 1:
        print("\nServers configuration:")
        print("Host: {0}".format(HOST))
        print("Port: {0}".format(PORT))
        print("Key: {0}".format(KEY["key"]))
        if KEY["key"] is not None:
            print("Key methods:")
            for method in KEY["methods"]:
                print(method, end=" ")
            print("")
        print("Supported versions:")
        for version in VERSIONS:
            print(version, end=" ")
        print("\nOptions:")
        print("0. Start")
        print("1. Host")
        print("2. Port")
        print("3. Key")
        print("4. Protocol versions")

        try:
            pick = input()
        except:
            print("Error! Shutting down the program!")
            sys.exit()
        try:
            if(int(pick)==0):
                return(HOST, PORT, VERSIONS, KEY)
            elif(int(pick)==1):
                HOST = DefineAddress()
            elif(int(pick)==2):
                PORT = DefinePort()
            elif(int(pick)==3):
                KEY = DefineKey()
            elif(int(pick)==4):
                VERSIONS = DefineVersion()
        except:
            print("Give a value between 0 and 4!")
            continue

# If error happens during processing of the request an error message will be send back to the client
def ErrorResponse(client, errorCode, version="1.0"):
    ERRORCODES = {"600":"Failure", 
    "601":"Bad Request", 
    "602":"Not Found", 
    "603":"Unsupported Version",
    "604":"File Listing Failed",
    "605":"File Upload Failed",
    "606":"File Download Failed", 
    "607":"File Deletion Failed", 
    "608":"Filename Required", 
    "609":"Size Required", 
    "610":"Forbidden Access"}

    response = "HADES/"+version+" ERROR "+errorCode+" "+ERRORCODES[errorCode]+"\r\n\r\n\r\n"
    SendResponse(client, response)

# If LIST method is used in the request
def ResponseToList(client, directory):
    response = "HADES/"+VERSION+" REPLY 102 "+directory+"\r\n"
    size = 0
    body = ""
    try:
        for path, subdirs, files in os.walk(directory):
            body += (path + "/\n") 
            for name in files:
                filePath = (os.path.join(path, name))
                try:
                    fileSize = os.stat(filePath)
                    fileSize = fileSize.st_size
                except NotADirectoryError:
                    fileSize = ""
                    pass
                body += (filePath+" "+str(fileSize)+"\n")
                size += len(body.encode("utf8"))
    except:
        ErrorResponse(client, "604")
        return
    response = response + "Size:" + str(size) + "\r\n\r\n" + body + "\r\n\r\n\r\n"
    SendResponse(client, response)

# If UPLOAD method is used in the request
def ResponseToUpload(client, directory, request):
    requestLineAndHeaders = request.split("\r\n")
    size = None
    filename = None

    for value in requestLineAndHeaders:
        if "Size:" in value:
            size = value.split(":")[1]
        if "Filename:" in value:
            filename = value.split(":")[1]
        if size != None and filename != None:
            break

    if size == None:
        ErrorResponse(client, "609")
        return
    elif filename == None:
        ErrorResponse(client, "608")
        return
    try:
        body = request.split("\r\n\r\n")[1].split("\r\n\r\n\r\n")[0]
        body = binascii.unhexlify(str(body))
    except:
        print("Double CRLF not found")
        ErrorResponse(client, "605")
        return
    try:
        print("Directory: "+directory+" Filename: "+filename)
        if directory == "..":
            directory = "../"
        if directory == ".":
            newFile = open(filename, "wb+")
        else:
            newFile = open(directory+filename, "wb+")
        newFile.write(body[:int(size)])
        newFile.close()
        print("File "+filename+" uploaded successfully to "+directory)
    except:
        print("Unable to upload file to server")
        ErrorResponse(client, "600")
        return
    response = ("HADES/"+VERSION+" REPLY 101 "+directory+filename+"\r\n\r\n\r\n")
    SendResponse(client, response)

# If DELETE method is used in the request
def ResponseToDelete(client, fileLocation):
    print(fileLocation)
    try:
        f = open(fileLocation,"r")
        f.close()
    except FileNotFoundError:
        ErrorResponse(client, "602")
        return
    except:
        ErrorResponse(client, "600")
        return
    try:
        os.remove(fileLocation)
    except:
        ErrorResponse(client, "607")
        return
    response = ("HADES/"+VERSION+" REPLY 101 "+fileLocation+"\r\n\r\n\r\n")
    SendResponse(client, response)

# If DOWNLOAD method is used in the request
def ResponseToDownload(client, fileLocation):
    try:
        with open(fileLocation, "rb") as fileToSend:
            body = fileToSend.read()
    except FileNotFoundError:
        print("File does not exist")
        ErrorResponse(client, "602")
        return
    except:
        print("File download failed")
        ErrorResponse(client, "606")
        return
    
    size = os.stat(fileLocation).st_size
    response = ("HADES/"+VERSION+" FILE 200 "+fileLocation+"\r\n")
    body = binascii.hexlify(body)
    body = str(body).lstrip("b").strip("'")
    if "/" in fileLocation:
        filename = fileLocation.split("/")
        filename = filename[-1]
    else:
        filename = fileLocation

    response += "Filename:"+filename+"\r\n"+"Size:"+str(size)+"\r\n\r\n"+body+"\r\n\r\n\r\n"
    SendResponse(client, response)

# Checking that request is in accordance with the protocol and performing actions depending on the method
def ParseRequest(client, request, VERSIONS, KEY):
    try:
        requestLine = request.split("\r\n")[0]
        parts = requestLine.split()
        method = parts[0]
        requestTarget = parts[1]
        hadesVersion = parts[2]
    except:
        print("Can't split the request to pieces")
        ErrorResponse(client, "601", VERSION)
        return

    if method not in VALID_HADES_METHODS:
        print("Wrong method",method,"used")
        ErrorResponse(client, "601", VERSION)
        return

    # Checking that / divides the protocol name and its version
    if "/" not in hadesVersion:
        print(" / missing from HADES-VERSION")
        ErrorResponse(client, "601")
        return

    (name, number) = hadesVersion.split("/")
    
    # Checking that protocol name is right
    if name != "HADES":
        print("Wrong protocol name")
        ErrorResponse(client, "601")
        return

    # Checking that version is supported 
    if number not in VERSIONS:
        print("Unsupported version")
        ErrorResponse(client, "603")
        return

    # If method is LIST    
    if method == "LIST":
        if KEY["key"] != None:
            if "LIST" in KEY["methods"]:
                if CheckKey(request, KEY):
                    ResponseToList(client, requestTarget)
                else:
                    ErrorResponse(client, "610")
                    return
            else:
                ResponseToList(client, requestTarget)
        elif KEY["key"] == None:
            ResponseToList(client, requestTarget)

    # If method is DELETE
    if method == "DELETE":
        if KEY["key"] != None:
            if "DELETE" in KEY["methods"]:
                if CheckKey(request, KEY):
                    ResponseToDelete(client, requestTarget)
                else:
                    ErrorResponse(client, "610")
                    return
            else:
                ResponseToDelete(client, requestTarget)
        elif KEY["key"] == None:
            ResponseToDelete(client, requestTarget)

    # If method is UPLOAD
    if method == "UPLOAD":
        if KEY["key"] != None:
            if "UPLOAD" in KEY["methods"]:
                if CheckKey(request, KEY):
                    ResponseToUpload(client, requestTarget, request)
                else:
                    ErrorResponse(client, "610")
                    return
            else:
                ResponseToUpload(client, requestTarget, request)
        elif KEY["key"] == None:
            ResponseToUpload(client, requestTarget, request)

    # If method is DOWNLOAD
    if method == "DOWNLOAD":
        if KEY["key"] != None:
            if "DOWNLOAD" in KEY["methods"]:
                if CheckKey(request, KEY):
                    ResponseToDownload(client, requestTarget)
                else:
                    ErrorResponse(client, "610")
                    return
            else:
                ResponseToDownload(client, requestTarget)
        elif KEY["key"] == None:
            ResponseToDownload(client, requestTarget)

# Checking that theres a key header which value corresponds to the value of servers key
def CheckKey(request, KEY):
    requestLineAndHeaders = request.split("\r\n")
    for line in requestLineAndHeaders:
        if "Key:" in line:
            key, value = line.split(":")
            if value == KEY["key"]:
                return 1
    return 0

# Sending response to client if processing of the request was succesful
def SendResponse(client, response):
    #client.sendall(response)
    print("Sending following response header to client "+str(client.getpeername())+":\n"+response.split("\r\n")[0]+"\n")
    client.sendall(response.encode("utf-8"))

# Setting up the server
def StartServer(HOST,PORT,KEY,VERSIONS):
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.bind((HOST,PORT))
    connection.listen(5)

    while True:
        print("Waiting for connection")
        (client, addr) = connection.accept()
        print("Connection from address: {0}".format(addr))
        request = client.recv(2048)
        try:
            while "\r\n\r\n\r\n" not in request.decode():
                request += client.recv(2048)
        except:
            print(request)
            print("Failed to receive data from address: {0}".format(addr))
            ErrorResponse(client, "600", VERSION)
            continue
        ParseRequest(client, request.decode("utf-8"), VERSIONS, KEY)
            
if __name__ == "__main__":
    HOST,PORT,KEY,VERSIONS = SetUpServer()
    StartServer(HOST,PORT,VERSIONS,KEY)
