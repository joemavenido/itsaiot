import zb_HandshakeHub
import clientEgress
import time
import rlinetest
import ReceiveV2
import threading
import binascii
#myMAC = b'\xff\xff\xff\xff\xff\xff\xff\xff'
myMAC = b'\x00\x13\xa2\x00\x40\xe7\x35\x3e'
psk = 'HkdW54vs4FrSUSAA'
#psk = '123456789abcde'

secret, nodeID = zb_HandshakeHub.zb_executeHandshake(myMAC,psk)

ReceiveV2.setCreds(secret,nodeID)

zb= zb_HandshakeHub.zb
zbLock = threading.Lock()

def publish(packet):
	eol = b'\r\n'
	zb.write(packet+eol)

def isMyPull(packet):
	dstNode = packet[3:4]
	print("DEBUG: isMyPull packet: ",binascii.hexlify(packet))
	if(packet[1:2]==b'\x02' and packet[3:4]==dstNode):
		return True
	else:
		print("DEBUG: isMyPull False: ",binascii.hexlify(packet[1:2]), " not ",binascii.hexlify(dstNode))
		return False

def Zpull(dest,payload):
	publish(clientEgress.clientEncapsulate(b'\x01',nodeID,dest,payload,secret))

def Npull(dest,payload):
	startTime = time.time()
	publish(clientEgress.clientEncapsulate(b'\x01',nodeID,dest,payload,secret))
	reply = rlinetest.newReadLine(zb,12)
	if not (reply==b''):
		data = ReceiveV2.Receive(reply[:-2])
	curTime = time.time()
	while(curTime - startTime <24):
		reply = rlinetest.newReadLine(zb,12)
		if not (reply==b''):
			data = ReceiveV2.Receive(reply[:-2])
			if(isMyPull(data)):
				print('Npull sucess: ',data)
		curTime = time.time()

def pull(dest,payload):
	global zbLock
	zbLock.acquire()
	publish(clientEgress.clientEncapsulate(b'\x01',nodeID,dest,payload,secret))
	reply = pullReceive()
	if(reply==None):
		print("pull request timed out")
		zbLock.release()
		return None
	print('pulled data is: ',int.from_bytes(reply, byteorder='big'))
	zbLock.release()
	#print('pulled payload is: ',payload)
	return reply

def pullReceive():
	startTime = time.time()
	buff = rlinetest.newReadLine(zb,12)
	print("PULLREC DEBUG")
	if not (buff==b''):
		data = ReceiveV2.Receive(buff[:-2])
	curTime = time.time()
	while(curTime - startTime <24):
		buff = rlinetest.newReadLine(zb,12)
		if not(buff==b''):
			print('buff is',buff[:-2])
			data = ReceiveV2.Receive(buff[:-2])
			if(isMyPull(buff)):
				return data
				#return buff[:-2]
		curTime = time.time()
	return None

def push(dest,payload):
	publish(clientEgress.clientEncapsulate(b'\x00',nodeID,dest,payload,secret))

def recPackets():
	global zbLock
	#global SERPORT
	#zb = serial.Serial('SERPORT', timeout=1)
	print("zb_recPackets")
	while True:
		try:
			zbLock.acquire()
			data = rlinetest.newReadLine(zb,5)
			if(data != b''):
				ReceiveV2.Receive(data[:-2])
			zbLock.release()
			#pass
			#temp = b'\x00' # find a better delay
			time.sleep(.5)
			#print('')
			#parsePacket = ReceiveV2.Receive(data)
			#parsePacket = ReceiveV2.Receive(data[:-2], nodeID, secret)
		except KeyboardInterrupt:
			sys.exit()

def hello():
	while True:
		time.sleep(10)
		publish(clientEgress.clientEncapsulate(b'\x05',nodeID,bytes([int(nodeID)]),b'\x00',secret))

def terminal():
	while True:
		service =''
		dest ='' 
		service = input("Service (Push, Pull): ")
		service = service.lower()
		while not (service == 'push' or service == 'pull'):
			service = input("Service (Push, Pull): ")
			service = service.lower()

		while not (dest.isdigit()):
			dest=input("Destination Node: ")
			
		payload = input("Payload: ")

		if(service =='push'):
			push(bytes([int(dest)]),payload.encode())

		if(service =='pull'):
			pull(bytes([int(dest)]),payload.encode())

t1 = threading.Thread(target=recPackets)
t1.daemon = True
t1.start()

t2 = threading.Thread(target = terminal)
t2.start()

# t3 = threading.Thread(target = hello)
# t3.daemon = True
# t3.start()

#push(b'\x03',b'lumos')
#pull(b'\x03',b'lumos')