import socket
import struct
import sys
import time


#creates packets of data to send
def createPacket(sequence_nunmber, ack_number, ack, syn, fin, payload):
    data = struct.pack('!I', sequence_nunmber)
    data += struct.pack('!I', ack_number)
    data += struct.pack("!c", ack)
    data += struct.pack("!c", syn)
    data += struct.pack("!c", fin)
    data += struct.pack('512s', payload)
    return data



#step 1 - create the socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


#Parse command line arguments
try:
    ip = sys.argv[1]
    port = int(sys.argv[2])
    logFile = sys.argv[3]
    file = open(logFile, "a")
except Exception as ex:
    print("Invalid command line arguments: Client.py <ip> <port> <log file>")
    print(ex)
    sys.exit(0)


#step 2 - Create address
server_addr = (ip, port)

#create struct
format = ""
#packedInfo = createPacket()




sock.close()
file.close()
