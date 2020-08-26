# -*- coding: utf-8 -*-

import socket
import sys
import os
import binascii

# DEFAULT VALUES
PROTOCOL="HADES/1.0"
HOST="localhost"
PORT=1716

# Used to define request method
def DefineMethod():
    method = input("Give method: ")
    return method

# Used to define request target
def DefineTarget():
    target = input("Give target: ")
    return target

# Used to define Protocol/version, for example HADES/2.0
def DefineProtocol():
    protocol = input("Give protocol: ")
    return protocol

# Used to define a filename for filename header
def DefineFilename():
    while 1:
        print("Add Filename header yes/no:")
        addHeader=input().lower()
        if addHeader in ("yes", "y"):
            print("Give filename: ")
            filename=input()
            if not filename:
                print("Give a valid filename!")
                continue
            else:
                try:
                    f = open(filename, "r")
                    return filename
                except FileNotFoundError:
                    print("File not found!")
                    continue
                except:
                    print("Unexpected error!")
                    continue
                f.close()
        elif addHeader in ("no", "n"):
            return None
        else:
            continue

# Used to define a key for key header
def DefineKey():
    while 1:
        print("Add Key header yes/no: ")
        addHeader=input().lower()
        if addHeader in ("y", "yes"):
            print("Give key: ")
            key=input()
            if not key:
                print("Give a valid key!")
                continue
            else:
                return key
        elif addHeader in ("n", "no"):
            return None
        else:
            continue

# Used to define a host for host header. Currently host header is not used anyway in the server side.
def DefineHost():
    while 1:
        print("Add host header yes/no")
        addHeader=input().lower()
        if addHeader in ("y", "yes"):
            print("Give Host: ")
            host=input()
            if not host:
                print("Give a valid host!")
                continue
            else:
                return host
        elif addHeader in ("n", "no"):
            return None
        else:
            continue

# Used to define host and port to connect 
def DefineHostAndPort(HOST, PORT):
    while 1:
        print("Using host:{0} and port {1} yes/no".format(HOST,PORT))
        pick = input()
        pick = pick.lower()
        if pick in ("y", "yes"):
            return HOST, PORT
        elif pick in ("n", "no"):
            print("Give new host: ")
            host=input()
            if not host:
                print("Give a valid host!")
                continue
            print("Give new port: ")
            port=input()
            if str(port).isdigit() and not None:
                PORT = int(port)
                HOST = host
                return HOST, PORT
            else:
                print("Give a valid port!")
                continue
        else:
            print("Give a valid host")
            continue

# User interface
def ModifyRequest(method="LIST", target=".", protocol=PROTOCOL):
    headers={"Filename":None, "Size":None, "Key":None, "Host":None}

    while 1:
        print("\nHost: {0} Port: {1}".format(HOST,PORT))
        print("Current request:")
        print("{0} {1} {2}".format(method, target, protocol))
        if(headers["Filename"]):
            filename = headers["Filename"].split("/")
            filename = filename[-1]
            print("Filename:{0}".format(filename))
            print("Size:{0}".format(headers["Size"]))
        if(headers["Key"]):
            print("Key:{0}".format(headers["Key"]))
        if(headers["Host"]):
            print("Host:{0}".format(headers["Host"]))

        print("\nOptions:")
        print("0. Send")
        print("1. Method")
        print("2. Target")
        print("3. Protocol")
        print("4. Filename")
        print("5. Key")
        print("6. Host")
        
        try:
            pick = input()
        except:
            print("Error! Shutting down the program!")
            sys.exit()

        if(int(pick)==0):
            return(method, target, protocol, headers)
        elif(int(pick)==1):
            method = DefineMethod()
        elif(int(pick)==2):
            target = DefineTarget()
        elif(int(pick)==3):
            protocol = DefineProtocol()
        elif(int(pick)==4):
            headers["Filename"] = DefineFilename()
            if headers["Filename"] is not None:
                size = os.stat(headers["Filename"])
                headers["Size"] = size.st_size
        elif(int(pick)==5):
            headers["Key"] = DefineKey()
        elif(int(pick)==6):
            headers["Host"] = DefineHost()
        else:
            print("Give proper value!")

# If UPLOAD method is used, Filename header is added to the request and files data is added to body
def UploadMethod(request, headers):
    body = ""
    try:
        with open(headers["Filename"], "rb") as fileToSend:
            body = fileToSend.read()
    except FileNotFoundError:
        print("File at path ",headers["Filename"]," not found!")
        sys.exit()
    except:
        print("Unable to read the file ",headers["Filename"])
        sys.exit()
    finally:
        if "/" in headers["Filename"]:
            filename = headers["Filename"].split("/")
            headers["Filename"] = filename[-1]
        else:
            filename = headers["Filename"]
        # Adding all the headers to request
        for header, value in headers.items():
            if value == None:
                continue
            else:
                request += header+":"+str(value)+"\r\n"
        # Adding files data to request body
        request += "\r\n"
        body = binascii.hexlify(body)
        body = str(body).lstrip("b").strip("'")
        request += str(body)
    fileToSend.close()
    request += "\r\n\r\n\r\n"
    return request      

# Performs actions depending on the method
def CreateRequest(method, target, protocol, headers):    
    request = (method+" "+target+" "+protocol+"\r\n")

    # Adding headers and files data to body if UPLOAD method is used   
    if headers["Filename"] is not None and method == "UPLOAD":
        request = UploadMethod(request, headers)
    # If LIST, DELETE, DOWNLOAD or any other value as method is used, we add headers to request
    else:
        for header, value in headers.items():
            if value == None:
                continue
            else:
                request += header+":"+str(value)+"\r\n"
        request += "\r\n\r\n"
    return request

# Used to send the request
def Send(HOST, PORT, request):
    try:
        connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        connection.connect((HOST,int(PORT)))
    except:
        print("Failed to make connection!")
        sys.exit()    
    connection.sendto(request.encode("utf-8"),(HOST, PORT))
    return connection

# Used to receive the response
def Receive(socket):

    response = b""
    while "\r\n\r\n\r\n" not in response.decode("utf-8"):
        data = socket.recv(4096)
        response += data
        if not data:
            break
    socket.close()

    response = response.decode("utf-8")
    responseMethod=response.split(" ")[1]
    responseCode=response.split(" ")[2]
    
    # If response method is ERROR
    if responseMethod == "ERROR":
        try:
            print(response.split("\r\n\r\n\r\n")[0])
        except:
            print(response)

    # If response method is FILE
    elif responseMethod == "FILE":
        filename = None
        size = None
        try:
            responseLineAndHeaders = response.split("\r\n\r\n")[0]
            body = response.split("\r\n\r\n")[1].split("\r\n\r\n\r\n")[0]
            body = binascii.unhexlify(str(body))
        except:
            print("Double CRLF not found!")
            sys.exit
        responseLineAndHeaders = responseLineAndHeaders.split("\r\n")
        headers = responseLineAndHeaders[0:]
        print(responseLineAndHeaders[0])
        for header in headers:
            keyAndValue = header.split(":")
            if keyAndValue[0] == "Filename":
                filename = keyAndValue[1]
            elif keyAndValue[0] == "Size":
                size = int(keyAndValue[1])
        if filename == None:
            print("Missing Filename header!")
            return
        elif size == None:
            print("Missing Size header!")
            return
        else:
            filename = filename.split("/")
            newFile = open(filename[-1], "wb+")
            newFile.write(body[:int(size)])
            newFile.close()
            print("File downloaded successfully!")
    
    # If response method is REPLY
    elif responseMethod == "REPLY":
        if responseCode == "100" or "101":
            print(response.split("\r\n\r\n\r\n")[0])
        elif responseCode == "102":
            try:
                responseLineAndHeaders = response.split("\r\n\r\n")[0]
                body = response[response.find("\r\n\r\n"):]
            except:
                print("CRLF not found!")
                sys.exit
            responseLineAndHeaders = responseLineAndHeaders.split("\r\n")
            print(responseLineAndHeaders[0])
            print("\n",body)
        
if __name__ == "__main__": 
    method,target,protocol,headers = ModifyRequest()
    HOST,PORT = DefineHostAndPort(HOST, PORT)
    request = CreateRequest(method, target, protocol, headers)
    connection = Send(HOST, PORT, request)
    Receive(connection)























