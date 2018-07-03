import rsa
from Crypto.Cipher import AES
import serial
import binascii
import time
from Crypto.Hash import MD5
import clientHandshake as handshake
import rlinetest

SERPORT = 'COM8'
#myMAC = b'\x00\x13\xa2\x00\x40\xe7\x35\x3e'
#myMAC = b'\xff\xff\xff\xff\xff\xff\xff\xff'
myMAC = ''
#psk = 'HkdW54vs4FrSUSAA'
zb  = serial.Serial(SERPORT,timeout=1)
def publish(data):
	#zb  = serial.Serial(SERPORT)
	eol = b'\r\n'
	print("sending(len:",len(binascii.hexlify(data)),") :",binascii.hexlify(data))
	zb.flush()	
	zb.write(data+eol)
	#zb.close()

def forMe(packet):
	global myMAC
	Pmac = packet[2:10]
	if(myMAC==Pmac):
		return True
	else:
		print("Packet MAC: ",binascii.hexlify(Pmac))
		print("MAC ADDRESS: ",binascii.hexlify(myMAC))
		return False

def receive():
	#zb  = serial.Serial(SERPORT,timeout=12)
	data = rlinetest.newReadLine(zb,12)
	#zb.flush()
	print("received: (len:",len(binascii.hexlify(data)),") :",binascii.hexlify(data))
	if not (data==None):
		if(forMe(data)):
			return data[:-2]
	return None

def zb_executeHandshake(mymac, psk):
	global myMAC
	myMAC = mymac
	secret = None
	nodeID = None
	p1 = handshake.phaseOne(mymac)
	publish(p1)
	p2 = receive()
	p3 = handshake.phaseTwo(p2,mymac)
	publish(p3)
	p4 = receive()
	p5 = handshake.phaseThree(p4,psk,mymac)
	publish(p5)
	p6 = receive()
	p7 = handshake.phaseFour(p6,psk,mymac)
	publish(p7)

	secret,nodeID = handshake.getCredentials()
	return (secret,nodeID)