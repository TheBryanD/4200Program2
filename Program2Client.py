import socket
import struct
import sys
import time
from collections import namedtuple

#creates packets of data to send
def createPacket(sequence_number, ack_number, ack, syn, fin, payload):
	try:
		data = struct.pack('!I', sequence_number)
		data += struct.pack('!I', ack_number)
		data += struct.pack('29s', ''.encode())
		data += struct.pack("!c", ack.encode())
		data += struct.pack("!c", syn.encode())
		data += struct.pack("!c", fin.encode())
		data += struct.pack('512s', payload.encode())
		return data
	except Exception as ex:
		print("Error creating packet: ", ex)

#step 1 - create the socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#Parse command line arguments
try:
    ip = sys.argv[1]
    port = int(sys.argv[2])
    logFile = sys.argv[3]
    file = open(logFile, "a")
except Exception as ex:
    print("Invalid command line arguments: Client.py <hostname/ip> <port> <logfile>")
    print(ex)
    sys.exit(0)

#step 2 - Create address
server_addr = (ip, port)
print("Server address: ", server_addr)
print("Server port: ", port)

def send(seq_num, ack_num, ack, syn, fin, data, addr):
	if(addr[0] != server_addr[0] and addr[1] != server_addr[1]):
		sys.exit(1)

	send_data = createPacket(seq_num, ack_num, ack, syn, fin, data)
	sock.sendto(send_data, server_addr)
	
def recv():
	data, addr = sock.recvfrom(1024)
	seq_num, ack_num, notUsed, ack, syn, fin = struct.unpack('II29sccc', data)
	if(data):
		print(data)
	else:
		time.sleep(2)
	return ack_num, seq_num, notUsed, ack, syn, fin, addr

seq_num = 12345
ack_num = 0
ack = 'N'
syn = 'Y'
fin = 'N'
data = " "

while True:
	try:
		if(seq_num == 12345):
			send(seq_num, ack_num, ack, syn, fin, data, server_addr)
			print("Data got sent")
			file.write("SEND ", seq_num, " ", ack_num, " ", ack, " ", syn, " ", fin)

			seq_num, ack_num, notUsed, ack, syn, fin, addr = recv()
			print("Data got receiv")
			file.write("RECV ", seq_num, " ", ack_num, " ", ack, " ", syn, " ", fin)

			ack_num += 1
			syn = 'N'
			send(seq_num, ack_num, ack, syn, fin, data, addr)
			file.write("SEND ", seq_num, " ", ack_num, " ", ack, " ", syn, " ", fin)
		else:
			seq_num, ack_num, notUsed, ack, syn, fin, addr = recv()
			file.write("RECV ", seq_num, " ", ack_num, " ", ack, " ", syn, " ", fin)

			if(fin == 'Y'):
				ack = 'Y'
				ack_num += 512
				send(seq_num, ack_num, ack, syn, fin, data, addr)
				file.write("SEND ", seq_num, " ", ack_num, " ", ack, " ", syn, " ", fin)
				exit()

			ack_num += 512
			send(seq_num, ack_num, ack, syn, fin, data, addr)
			file.write("SEND ", seq_num, " ", ack_num, " ", ack, " ", syn, " ", fin)

	except KeyboardInterrupt:
		sock.close()
		file.close()
	except:
		sock.close()
		file.close()

#create struct
#format = ""
#packedInfo = createPacket()

#sock.close()
#file.close()