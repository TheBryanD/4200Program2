import socket
from socket import RCVALL_IPLEVEL
import struct
import sys
import time
import urllib.request, urllib.error, urllib.parse
from typing import Sequence


#creates packets of data to send
def createPacket(sequence_nunmber, ack_number, ack, syn, fin):
    data = struct.pack('32s', sequence_nunmber)
    data += struct.pack('32s', ack_number)
    data += struct.pack('29s', '')
    data += struct.pack("!c", ack)
    data += struct.pack("!c", syn)
    data += struct.pack("!c", fin)
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
opener = urllib.request.FancyURLopener({})
f = opener.open(webpageToDownload)
content = f.read()
localWebFileSave = open('C:\\Sample Files\\webpage.html', 'w').write(str(content))
#response = urllib.request.urlopen(webpageToDownload)
#webcontent = response.read()
#localWebFileSave = open('webPage.html', 'wb').write(webcontent)
#localWebFileSave.close()
print(str(webpageToDownload) + " was saved to local storage.")

#step 3 - specify where the server should listen on, IP and port
server_addr_obj = ('127.0.0.1', int(port))
sock.bind(server_addr_obj)
print("Address : ", server_addr_obj)
print("Port : ", port)

while True:
    try:
    #Receive data from client
        recvData, addr = sock.recvfrom(1024)
        unpacker = struct.Struct('32s32s29sccc')
        unpacker.unpack(recvData)

        #send data back to client and log
        if int(recvData[0]) == 12345:
            #send ack handshake packet
            if recvData[4] == 'Y':
                syn = 'Y'
            else: 
                syn = 'N'
            sqnc_num = int(recvData[0])
            header = createPacket(100, sqnc_num+1, 'Y', syn, 'N')
            sock.sendto(addr, header)

            file.write("RECV ", sqnc_num, " ", recvData[1], " ", recvData[3], " ", recvData[4], " ", recvData[5])
            file.write("SEND ", 100, " ", sqnc_num+1, " ", 'Y', " ", syn, " ", 'N')
        else:
            isLastPacket = False
            #create packet to send back
            sqnc_num = recvData[1] +1
            ack_num = recvData[0] +1
            ack = 'Y'
            syn = 'N'
            if isLastPacket == True:
                fin = 'Y'
            else:
                fin = 'N'
            header = createPacket(sqnc_num, ack_num, ack, syn, fin)
            sock.sendto(header, addr)

            file.write("RECV ", sqnc_num, " ", recvData[1], " ", recvData[3], " ", recvData[4], " ", recvData[5])
            file.write("SEND ", ack_num, " ", sqnc_num+1, " ", ack, " ", syn, " ", fin)

        #print data to screen
        if(recvData):
            print(recvData)
        else:
            time.sleep(2)


    except KeyboardInterrupt: #CTRL+^C
        sock.close()
        file.close()
    except:
        sock.close()
        file.close()