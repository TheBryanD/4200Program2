import socket
import struct
import sys
import time
 
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
    file = open(logFile, "w")
except Exception as ex:
    print("Invalid command line arguments: Client.py <hostname/ip> <port> <logfile>")
    print(ex)
    sys.exit(-1)

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
	unpacker = struct.Struct('!II29sccc512s')
	unpackedData = unpacker.unpack(data)
	return unpackedData, addr

seq_num = 12345
ack_num = 0
ack = 'N'
syn = 'Y'
fin = 'N'
data = " "
finished = True

while finished:
	try:
		if(seq_num == 12345):
			send(seq_num, ack_num, ack, syn, fin, data, server_addr)
			try:
				file.write("SEND " + str(seq_num) + " " + str(ack_num) + " " + ack + " " + syn + " " + fin + '\n')
			except Exception as ex:
				print(ex)
				exit()
			unpackedData, addr = recv()
			seq_num = int(unpackedData[1])
			ack_num = int(unpackedData[0])
			#!!!!! change indexes
			ack = unpackedData[3].decode()
			syn = unpackedData[4].decode()
			fin = unpackedData[5].decode()

			try:
				file.write("RECV " + str(ack_num) + " " + str(seq_num) + " " + ack + " " + syn + " " + fin + '\n')
			except Exception as ex:
				print(ex)
				exit()

			ack_num += 1
			syn = 'N'

			try:
				send(seq_num, ack_num, ack, syn, fin, data, server_addr)
			except Exception as ex:
				print(ex)

			file.write("SEND " + str(seq_num) + " " + str(ack_num) + " " + ack + " " + syn + " " + fin + '\n')

		else:
			unpackedData, addr = recv()
			seq_num = int(unpackedData[1])
			ack_num = int(unpackedData[0])
			ack = unpackedData[3].decode()
			syn = unpackedData[4].decode()
			fin = unpackedData[5].decode()
			payload = unpackedData[6].decode()

			try:
				file.write("RECV " + str(ack_num) + " " + str(seq_num) + " " + ack + " " + syn + " " + fin + '\n')
			except Exception as ex:
				print(ex)

			if(fin == 'Y'):
				ack = 'Y'
				finished = False

			ack_num += 512
			send(seq_num, ack_num, ack, syn, fin, data, addr)
			file.write("SEND " + str(seq_num) + " " + str(ack_num) + " " + ack + " " + syn + " " + fin + '\n')

	except KeyboardInterrupt:
		sock.close()
		file.close()
	except:
		sock.close()
		file.close()