import socket
import struct
import sys
import time
import urllib.request, urllib.error, urllib.parse
from typing import Sequence


#creates packets of data to send
def createPacket(sequence_nunmber, ack_number, ack, syn, fin, payload):
    data = struct.pack('!I', sequence_nunmber)
    data += struct.pack('!I', ack_number)
    data += struct.pack("!c", ack)
    data += struct.pack("!c", syn)
    data += struct.pack("!c", fin)
    data += struct.pack('512s', payload)
    return data


port = 0

#step 1 - create the socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#Parse command line arguments
try:
    port = sys.argv[1]
    logFile = sys.argv[2]
    webpageToDownload = sys.argv[3]
    file = open(logFile, "a")
except:
    print("Invalid command line arguments: Server.py <port> <logFile> <webpage>")
    sys.exit(0)

#step 2 - save webpage
response = urllib.request.urlopen(webpageToDownload)
webcontent = response.read()
localWebFileSave = open('webPage.html', 'wb').write(webcontent)
localWebFileSave.close()
print(str(webpageToDownload) + " was saved to local storage.")

#step 3 - specify where the server should listen on, IP and port
server_addr_obj = ('127.0.0.1', int(port))
sock.bind(server_addr_obj)
print("Address : ", server_addr_obj)
print("Port : ", port)

while True:
    #step 4 - create data to send
    try:
        data = ''
        send_data = createPacket(100, 0, 'Y', 'N', 'N', data)

    #step 5 - send data to client
        data, addr = sock.recvfrom(1024)
        sock.sendto(addr, send_data)
        unpacker = struct.Struct('iii8s')

        if(data):
            print(data)
        else:
            time.sleep(2)
    except KeyboardInterrupt: #CTRL+^C
        sock.close()
        file.close()
    except:
        sock.close()
        file.close()