import socket
import sys
from threading import Thread
import json
from subprocess import Popen, PIPE
import re
from time import sleep

def acquire_MAC_addr(IP):
    pid = Popen(["ip", "neigh", "show", IP], stdout=PIPE)
    str = pid.communicate()[0]
    str = str.decode()
    if len(str) == 0:
        return None
    MAC = re.search(r"(([a-f\d]{1,2}\:){5}[a-f\d]{1,2})", str).groups()[0]
    return MAC

def check_webServer(client_addr):
    if client_addr == "127.0.0.1":  # this should be the ip address of web server
        MAC = acquire_MAC_addr(client_addr)
        if MAC is not None and MAC == "F8:A2:D6:C0:FB:ED": # the MAC addr of the web server's host
            return True
    return False

def worker_service(newSocket, destAddr):
    #while True:

    buf = newSocket.recv(1024)
    buf = buf.decode()
    dict_data = json.loads(buf)
        #print(dict_data)

    print("The data from " + str(destAddr[0]) + " is " + str(dict_data))

    reply = {"status": True}
    reply = json.dumps(reply)
    newSocket.send(reply.encode())
        #print("worker for" + str(destAddr[0]) + "complete")
        # return buf
        # sock.close()


if __name__ == '__main__':
    while True:
        try:
            gw_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            gw_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            gw_server.bind(('127.0.0.1', 9906))  # should be binding the ip addr of router

            gw_server.listen(5)
        except socket.error as msg:
            print(msg)
            sys.exit(1)
        try:
            print("Wait for Connection..................")
            while True:
                print("waiting for client:")
                newSocket, destAddr = gw_server.accept()
                worker = Thread(target=worker_service, args=(newSocket, destAddr))
                worker.start()
                # worker.join()

        finally:
            gw_server.close()
    #socket_service_data()
