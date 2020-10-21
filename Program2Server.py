from os import read
import socket
import struct
import sys
from sys import getsizeof
import time
import urllib.request, urllib.error, urllib.parse
from typing import Sequence
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
"""
used to debug and see each packet payload
i =0
for chunk in chunks:
    print(str(i) + ": " + str(chunk))
    i += 1
exit()
"""

#step 3 - specify where the server should listen on, IP and port
server_addr_obj = ('localhost', int(port))
sock.bind(server_addr_obj)
print("Address : ", server_addr_obj)
print("Port : ", port)

while True:
    try:
    #Receive data from client
        recvData, addr = sock.recvfrom(1024)
        #print("Data received: " + str(recvData))
        unpacker = struct.Struct('!II29sccc512s')
        print("Unpacker created")
        unpackedData = unpacker.unpack(recvData)
        print("Received: ")
        #Easier to read Info
        unpack1 = unpackedData[0]
        unpack2 = unpackedData[1]
        unpack3 = unpackedData[3].decode()
        unpack4 = unpackedData[4].decode()
        unpack5 = unpackedData[5].decode()
        unpack6 = unpackedData[6].decode()
        print(str(unpack1) + " " + str(unpack2) + " " + str(unpack3) + " " + str(unpack4) + " " + str(unpack5) + " " + unpack6)

        #If last packet was received (Fin == 'Y'), Log the info and start the loop again
        if unpack5 == 'Y':
            file.write("RECV " + str(sqnc_num) + " " + str(unpackedData[1]) + " " + unpackedData[3].decode() + " " + unpackedData[4].decode() + " " + unpackedData[5].decode() + '\n')
            #close then reopen file to save what was logged
            file.close()
            file = open(logFile, "a")
            continue
        
        #If packets ack isnt the ack expected, and its not the handshake packet, wait 0.5sec and send again
        if unpack1 != ackNumToCompare and int(unpack1) != 12345:
            sock.sendto(header, addr)
            print("Error, RETRANSMITTING...")
            time.sleep(0.5)
            file.write("RETRANS " + str(sqnc_num) + " " + str(unpackedData[1]) + " " + unpackedData[3].decode() + " " + unpackedData[4].decode() + " " + unpackedData[5].decode() + '\n')

        #send data back to client and log
            #If a handshake packet
        if int(unpackedData[0]) == 12345:
            #send ack handshake packet
            print("This packet was a handshake packet")
            if unpackedData[4].decode() == 'Y':
                print("syn: Y")
                syn = 'Y'
            else: 
                print("syn: N")
                syn = 'N'
            
            #Create Packet to send
            sqnc_num = unpackedData[0]
            ackNumToCompare = unpackedData[0]+1
            print("Creating Header")
            header = createPacket(100, sqnc_num+1, 'Y', syn, 'N', "")
            print("Sending header: " + str(header))

            #send
            sock.sendto(header, addr)
            print("HeaderSent")
            print("Sent: " + str(header)) 

            #Log the info
            file.write("RECV " + str(sqnc_num) + " " + str(unpackedData[1]) + " " + unpackedData[3].decode() + " " + unpackedData[4].decode() + " " + unpackedData[5].decode() + '\n')
            file.write("SEND " + str(100) + " " + str((sqnc_num+1)) + " " + 'Y' + " " + syn + " " + 'N' + '\n')
            print("Logged data and finished first loop")
            print("Trying to receive data: ")

            #If not a handshake packet
        else:
            print("This packet was not a handshake packet")
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
            print("Creating Header")

            #Create 512 bytes of the file to send as the payload
            #try:
            chunk = chunks[payloadIterator]
            data.close()
            #except IndexError:
            #    print("Index out of bounds while creating chunks")
            # except Exception as ex:
            #    print(ex)

            #Create packet to send back
            header = createPacket(sqnc_num, ack_num, ack, syn, fin, chunk)

            #Send to client
            print("Sending Header " + str(sqnc_num) +" "+ str(ack_num) +" "+ ack + " " + syn + " " + fin + " ")
            sock.sendto(header, addr)
            print("Header sent")

            #Log info 
            file.write("RECV " + str(ack_num-1) + " " + str(sqnc_num) + " " + unpackedData[3].decode() + " " + unpackedData[4].decode() + " " + unpackedData[5].decode() + '\n')
            file.write("SEND " + str(sqnc_num) + " " + str((ack_num)) + " " + ack + " " + syn + " " + fin + '\n')
            #iteration +=1 
            payloadIterator += 1

            #Check and see if this is the last packet to send to the client
                #If it is last packet, reset variables
            if isLastPacket == True:
                payloadIterator = 0
                isLastPacket = False
 
                #If not last packet, Continue looping with variables the way they are
            else:
                print("finishing loop and doing again")
                print("Trying to receive Data: ")



    except KeyboardInterrupt: #CTRL+^C
        sock.close()
        file.close()
    except:
    #except Exception as ex:
        #print("Error: ", ex)
        sock.close()
        file.close()