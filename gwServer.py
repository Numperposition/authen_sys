import socket
import sys
from threading import Thread
import json
from subprocess import Popen, PIPE
import re
from time import sleep

online_list = []

def firewall_cleaner():
    while True:
        sleep(3)
        filename = "arp"                                 #"/proc/net/arp"
        arp_list = []
        with open(filename, 'r') as file:
            line = file.readline() # jump over first line
            while line:
                line = file.readline()
                if line == "":
                    break
                arp_list.append(line)
        if len(arp_list) != 0:
            for line in arp_list:
                flag = line[29:32]
                mac = line[41:58]
                print("flag = " + flag)
                print("mac = " + mac)
                if mac in online_list and flag != "0x2":
                    pid = Popen(["iptables", "-D", "FORWARD", "-m", "mac", "--mac-source", mac, "-j", "ACCEPT"],stdout=PIPE)
                    bytes = pid.communicate()[0]
                    if len(bytes) == 0:
                        print("firewall rule for ", mac, "deleted.")

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
        if MAC is not None and MAC == "f8:a2:d6:c0:fb:ed": # the MAC addr of the web server's host
            return True
    return False

def process_firewall(IP):
    print("IP is ", IP)
    MAC = acquire_MAC_addr(IP)
    if MAC == None:
        return False
    if MAC in online_list:
        print(MAC ,"alreadly have link to outside network")
        return True
    pid = Popen(["iptables", "-I", "FORWARD", "-m", "mac", "--mac-source", MAC, "-j", "ACCEPT"], stdout=PIPE)
    bytes = pid.communicate()[0]
    if len(bytes) == 0:
        print("open link for device: ", MAC)
        online_list.append(MAC)
        return True

    return False


def worker_service(newSocket, destAddr):
    #while True:

    buf = newSocket.recv(1024)
    buf = buf.decode()
    dict_data = json.loads(buf)
        #print(dict_data)

    print("The data from " + str(destAddr[0]) + " is " + str(dict_data))
    if process_firewall(dict_data['ip']) == False:
        reply = {"status": False}
    else:
        reply = {"status": True}
    reply = json.dumps(reply)
    newSocket.send(reply.encode())
        #print("worker for" + str(destAddr[0]) + "complete")
        # return buf
        # sock.close()


if __name__ == '__main__':
    cleaner = Thread(target=firewall_cleaner)
    cleaner.start()
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
                if check_webServer(str(destAddr[0])) == False: # check whether the source is from web server
                    break
                worker = Thread(target=worker_service, args=(newSocket, destAddr))
                worker.start()
                # worker.join()

        finally:
            gw_server.close()
    #socket_service_data()

# note: firewall.user should initial as: iptables -I FORWARD -s 192.168.1.1/24 -j REJECT
# iptables -I FORWARD -s 192.168.1.100 -j ACCEPT