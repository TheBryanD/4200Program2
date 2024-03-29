from os import read
import socket
import struct
import sys
from sys import getsizeof
import time
import urllib.request, urllib.error, urllib.parse
from typing import Sequence


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

#step 3 - specify where the server should listen on, IP and port
server_addr_obj = ('localhost', int(port))
sock.bind(server_addr_obj)
print("Address : ", server_addr_obj)
print("Port : ", port)

while True:
    try:
    #Receive data from client
        recvData, addr = sock.recvfrom(1024)
        print("Data received")
        unpacker = struct.Struct('!II29sccc512s')
        print("Unpacker created")
        unpackedData = unpacker.unpack(recvData)
        print("Received: ", unpackedData)

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
            header = createPacket(100, sqnc_num+1, 'Y', syn, 'N', "")
            print("Sending header: " + str(header))
            try:
                sock.sendto(header, addr)
            except:
                print("Error occurred, retransmitting")
                file.write("RETRANS " + str(sqnc_num) + " " + str(unpackedData[1]) + " " + unpackedData[3].decode() + " " + unpackedData[4].decode() + " " + unpackedData[5].decode() + '\n')
                sock.sendto(header, addr)
            print("HeaderSent")
            print("Sent: " + str(header)) 

            file.write("RECV " + str(sqnc_num) + " " + str(unpackedData[1]) + " " + unpackedData[3].decode() + " " + unpackedData[4].decode() + " " + unpackedData[5].decode() + '\n')
            file.write("SEND " + str(100) + " " + str((sqnc_num+1)) + " " + 'Y' + " " + syn + " " + 'N' + '\n')
            print("Logged data and finished first loop")
            print("Trying to receive data: ")
        else:
            isLastPacket = False
            print("This packet was not a handshake packet")
            #create packet to send back
            sqnc_num = unpackedData[1]+1
            ack_num = unpackedData[0]+1
            ack = 'Y'
            syn = 'N'
            if isLastPacket == True:
                fin = 'Y'
            else:
                fin = 'N'
            print("Creating Header")

            #Create 512 bytes of the file to send as the payload
            try:
                data = open('C:\\Sample Files\\webpage.html', 'r')
                chunk = data.read(512)
                if not chunk:
                    isLastPacket = True
                    exit()
                header = createPacket(sqnc_num, ack_num, ack, syn, fin, chunk)
                data.close()
            except Exception as ex:
                print(ex)
                exit(1)

            #Send to client and log
            print("Sending Header " + str(sqnc_num) +" "+ str(ack_num) +" "+ ack + " " + syn + " " + fin + " ")
            try:
                sock.sendto(header, addr)
            except:
                print("Error occurred, retransmitting")
                file.write("RETRANS " + str(sqnc_num) + " " + str(unpackedData[1]) + " " + unpackedData[3].decode() + " " + unpackedData[4].decode() + " " + unpackedData[5].decode() + '\n')
            print("Header sent")

            file.write("RECV " + str(ack_num-1) + " " + str(sqnc_num-1) + " " + unpackedData[3].decode() + " " + unpackedData[4].decode() + " " + unpackedData[5].decode() + '\n')
            file.write("SEND " + str(sqnc_num) + " " + str((ack_num)) + " " + ack + " " + syn + " " + fin + '\n')
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