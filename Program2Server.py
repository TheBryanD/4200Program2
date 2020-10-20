import socket
import struct
from struct import unpack
import sys
import time
import urllib.request, urllib.error, urllib.parse
from typing import Sequence


#creates packets of data to send
def createPacket(sequence_nunmber, ack_number, ack, syn, fin, payload):
    try:
        data = struct.pack('!I', sequence_nunmber)
        data += struct.pack('!I', ack_number)
        data += struct.pack('29s', '')
        data += struct.pack("!c", ack)
        data += struct.pack("!c", syn)
        data += struct.pack("!c", fin)
        data += struct.pack('512s', payload)
        return data
    except Exception as ex:
        print("Error creating packet: ", + ex)


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
server_addr_obj = ('localhost', int(port))
sock.bind(server_addr_obj)
print("Address : ", server_addr_obj)
print("Port : ", port)

while True:
    try:
    #Receive data from client
        recvData, addr = sock.recvfrom(1024)
        print("received data")
        unpacker = struct.Struct('II29sccc512s')
        print("unpacker created")
        unpackedData = unpacker.unpack(recvData)
        print("received: ", unpackedData)
        #send data back to client and log
        if int(unpackedData[0]) == 12345:
            #send ack handshake packet
            print("This packet was a handshake packet")
            if unpackedData[4].decode() == 'Y':
                print("syn: Y")
                syn = 'Y'
            else: 
                print("syn: N")
                syn = 'N'
            sqnc_num = unpackedData[0]
            print("Creating Header")
            header = createPacket(100, sqnc_num+1, 'Y', syn, 'N')
            print("Sending header")
            sock.sendto(addr, header)
            print("HeaderSent")

            file.write("RECV ", sqnc_num, " ", unpackedData[1], " ", unpackedData[3], " ", unpackedData[4], " ", unpackedData[5])
            file.write("SEND ", 100, " ", sqnc_num+1, " ", 'Y', " ", syn, " ", 'N')
        else:
            isLastPacket = False
            print("This packet was not a handshake packet")
            #create packet to send back
            sqnc_num = unpackedData[1] +1
            ack_num = unpackedData[0] +1
            ack = 'Y'
            syn = 'N'
            if isLastPacket == True:
                fin = 'Y'
            else:
                fin = 'N'
            header = createPacket(sqnc_num, ack_num, ack, syn, fin)
            sock.sendto(header, addr)

            file.write("RECV ", sqnc_num, " ", unpackedData[1], " ", unpackedData[3], " ", unpackedData[4], " ", unpackedData[5])
            file.write("SEND ", ack_num, " ", sqnc_num+1, " ", ack, " ", syn, " ", fin)

        #print data to screen
        if(unpackedData):
            print(unpackedData)
        else:
            time.sleep(2)


    except KeyboardInterrupt: #CTRL+^C
        sock.close()
        file.close()
    except Exception as ex:
        print("Error: ", ex)
        sock.close()
        file.close()