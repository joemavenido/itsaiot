#import RPi.GPIO as GPIO
#import Adafruit_DHT
from Crypto.Hash import MD5
import serial
import binascii
import time
import zb_HandshakeHub
#import clientEgress
#import ReceiveV2

zb = zb_HandshakeHub.zb

def Push(payload):
	#GPIO.setmode(GPIO.BCM)
	#GPIO.setup(4, GPIO.OUT)

	if(payload.decode() == 'lumos'):
		print('DEBUG: light is on')
	#	GPIO.output(4, 1)
	else:
		print('DEBUG: light is off')
	#	GPIO.output(4, 0)
	print("PUSH RECEIVED: PAYLOAD IS ", payload)



# def PullReq(parsePacket):

# 	hum, temp = 22,45
# 	hum = int(hum)
# 	temp = int(temp)
# 	packet = clientEgress.clientEncapsulate(b'\x02',parsePacket['src'],parsePacket['dest'],temp,ReceiveV2.secret)
# 	publish(packet)

def PullRep(payload):

	print("pull replied: ",int.from_bytes(payload,byteorder='big'))

def PullReq(parsePacket, secret, zb):
	#hum, temp = Adafruit_DHT.read_retry(11, 4)
	hum ,temp = 22,45
	hum = int(hum)
	temp = int(temp)
	pullreq = parsePacket['Payload']
	pullreq = (pullreq.decode()).lower()
	if (pullreq == 'temp'):
		pullrep = bytes([temp])
		print("MY TEMP IS: ", temp)
	elif (pullreq == 'humidity'):
		pullrep = bytes([hum])
		print("MY HUMIDITY IS: ", hum)
	header = b'\x01\x02'+parsePacket['dst'] +parsePacket['src'] + pullrep
	temp = header + secret
	ht = MD5.new()
	ht.update(temp)
	final = ht.hexdigest()
	data = header + bytes.fromhex(final)
	eol = b'\r\n'
	print("sending(len:",len(binascii.hexlify(data)),") :",binascii.hexlify(data))
	#time.sleep(4)	
	zb.write(data+eol)

#def PullRep(payload):

#def DataSend(payload):

#def DataCollect(payload):


def service(parsePacket, secret):
	global zb
	servType = parsePacket['Type']
	payload = parsePacket['Payload']

	if(servType == b'\x00'):
		Push(payload)
	elif(servType == b'\x01'):
		PullReq(parsePacket, secret, zb)
	elif(servType == b'\x02'):
		PullRep(payload)
	elif(servType == b'\x03'):
		DataSend(payload)
	elif(servType == b'\x04'):
		DataCollect(payload)

	return None
