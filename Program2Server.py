from os import read
import socket
import struct
import sys
from sys import getsizeof
import time
import urllib.request, urllib.error, urllib.parse
import math

#creates packets of data to send
def createPacket(sequence_nunmber, ack_number, ack, syn, fin, payload):
    try:
        data = struct.pack('!I', sequence_nunmber)
        data += struct.pack('!I', ack_number)
        data += struct.pack('29s', ''.encode())
        data += struct.pack("!c", ack.encode())
        data += struct.pack("!c", syn.encode())
        data += struct.pack("!c", fin.encode())
        data += struct.pack('512s', payload.encode())
        return data
    except Exception as ex:
        print("Error creating packet: " + ex)


port = 0
seekFrom = 0
chunks = []
payloadIterator = 0
isLastPacket = False
ackNumToCompare = 12345

#step 1 - create the socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#Parse command line arguments
try:
    port = int(sys.argv[1])
    logFile = sys.argv[2]
    webpageToDownload = sys.argv[3]
    file = open(logFile, "w")
except:
    print("Invalid command line arguments: Server.py <port> <logFile> <webpage>")
    sys.exit(-1)

#step 2 - save webpage
opener = urllib.request.FancyURLopener({})
f = opener.open(webpageToDownload)
content = f.read()
localWebFileSave = open('C:\\Sample Files\\webpage.html', 'w').write(str(content))
print(str(webpageToDownload) + " was saved to local storage.")
sizeOfHtml = getsizeof(open('C:\\Sample Files\\webpage.html', 'r').read())
print("size of html in bytes: " + str(sizeOfHtml))
size = 0
i = 0
data = open("C:\\Sample Files\\webpage.html", 'r')
while size < sizeOfHtml:
    chunks.append( data.read(512))
    size += 512
    i += 1
data.close()
totalNumIteration = int(math.ceil(sizeOfHtml/512))

#step 3 - specify where the server should listen on, IP and port
server_addr_obj = ('localhost', int(port))
sock.bind(server_addr_obj)
print("Address : ", server_addr_obj)
print("Port : ", port)

while True:
    try:
        #Receive data from client
        recvData, addr = sock.recvfrom(1024)
        unpacker = struct.Struct('!II29sccc512s')
        unpackedData = unpacker.unpack(recvData)

        #Easier to read Info
        unpack1 = unpackedData[0]
        unpack2 = unpackedData[1]
        unpack3 = unpackedData[3].decode()
        unpack4 = unpackedData[4].decode()
        unpack5 = unpackedData[5].decode()
        unpack6 = unpackedData[6].decode()

        file.write("RECV " + str(unpack1) + " " + str(unpack2) + " " + unpack3 + " " + unpack4 + " " + unpack5 + '\n')

        #If last packet was received (Fin == 'Y'), Restart the logs and start the loop again
        if unpack5 == 'Y':
            #close then reopen file to save what was logged
            file.close()
            file = open(logFile, "a")
            continue
        
        #If packets ack isnt the ack expected, and its not the handshake packet, wait 0.5sec and send again
        if unpack1 != ackNumToCompare and int(unpack1) != 12345:
            sock.sendto(header, addr)
            print("Error, RETRANSMITTING...")
            time.sleep(0.5)
            file.write("RETRANS " + str(sqnc_num) + " " + str(unpackedData[0]) + " " + unpackedData[3].decode() + " " + unpackedData[4].decode() + " " + unpackedData[5].decode() + '\n')

        #send data back to client and log
            #If a handshake packet
        if int(unpackedData[0]) == 12345:
            #send ack handshake packet
            if unpackedData[4].decode() == 'Y':
                syn = 'Y'
            else:
                syn = 'N'
            
            #Create Packet to send
            sqnc_num = unpackedData[0]
            ackNumToCompare = unpackedData[0]+1
            header = createPacket(100, sqnc_num+1, 'Y', syn, 'N', "")

            #send
            sock.sendto(header, addr)

            #Log the info
            file.write("SEND " + str(100) + " " + str((sqnc_num+1)) + " " + 'Y' + " " + syn + " " + 'N' + '\n')

            #If not a handshake packet
        else:
            #create packet to send back
            if unpackedData[1] == 101:
                sqnc_num = unpackedData[1]+1
            else:
                sqnc_num = unpackedData[1]
            ack_num = unpackedData[0]+1
            ackNumToCompare = unpackedData[0]+1
            ack = 'Y'
            syn = 'N'
            if payloadIterator+2 == totalNumIteration:
                isLastPacket = True
            if isLastPacket == True:
                fin = 'Y'
            else:
                fin = 'N'

            #Create 512 bytes of the file to send as the payload
            chunk = chunks[payloadIterator]
            data.close()

            #Create packet to send back
            header = createPacket(sqnc_num, ack_num, ack, syn, fin, chunk)

            #Send to client
            sock.sendto(header, addr)

            #Log info 
            file.write("SEND " + str(sqnc_num) + " " + str((ack_num)) + " " + ack + " " + syn + " " + fin + '\n')
            payloadIterator += 1

            #Check and see if this is the last packet to send to the client
                #If it is last packet, reset variables
            if isLastPacket == True:
                payloadIterator = 0
                isLastPacket = False
 
                #If not last packet, Continue looping with variables the way they are
            else:
                pass

    except KeyboardInterrupt: #CTRL+^C
        file.close()
        sock.close()
    except:
        file.close()
        sock.close()