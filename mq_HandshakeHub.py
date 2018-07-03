import rsa
from Crypto.Cipher import AES
import pika
import binascii
import time
from Crypto.Hash import MD5
import clientHandshake as handshake
import rlinetest

BROKER = '192.168.1.9'
myMAC = b'\x00\x00\x84\xef\x18\x46\x24\x2b'
psk = 'HkdW54vs4FrSUS2Y'

expectedPhase = 1

def on_timeout():
	print("timeout reached")
	global connection
	connection.close()

def publish(data):
	print("sending: :",binascii.hexlify(data))
	connection = pika.BlockingConnection(pika.ConnectionParameters(host=BROKER))
	channel = connection.channel()
	channel.exchange_declare(exchange='serverHand',exchange_type='fanout')
	channel.basic_publish(exchange='serverHand',routing_key='',body=data)
	connection.close()

def forMe(packet):
	global myMAC
	Pmac = packet[2:10]
	if(myMAC==Pmac):
		return True
	else:
		print("Packet MAC: ",binascii.hexlify(Pmac))
		print("MAC ADDRESS: ",binascii.hexlify(myMAC))
		return False

def getPhase(packet):
	phase =-1
	phase = int.from_bytes(packet[1:2],byteorder='big')
	return phase

def callme(ch, method, properties, body):

	global expectedPhase
	global psk
	global secret
	global nodeID
	incomingPhase=getPhase(body)
	print("server sent: ",binascii.hexlify(body))
	if(forMe(body) and expectedPhase==incomingPhase and incomingPhase==1):
		print("runningTwo")
		publish(handshake.phaseTwo(body,myMAC))
		expectedPhase+=1
		#ch.stop_consuming()
	if(forMe(body) and expectedPhase==incomingPhase and incomingPhase==2):
		print("runningThree")
		publish(handshake.phaseThree(body,psk,myMAC))
		expectedPhase+=1
		#ch.stop_consuming()
	if(forMe(body) and expectedPhase==incomingPhase and incomingPhase==3):
		print("runningFour")
		publish(handshake.phaseFour(body,psk,myMAC))
		#publish(nxt)
		expectedPhase+=1
	# 	#ch.stop_consuming()
	# if(forMe(body) and expectedPhase==incomingPhase and incomingPhase==4):
	# 	nodeID = phaseFive(body)
	# 	#publish(phaseFive(body))
	# 	expectedPhase+=1
		print("line 72")
		ch.stop_consuming()

'''
p1 = handshake.phaseOne(myMAC)
	publish(p1)
	p2 = receive()
	p3 = handshake.phaseTwo(p2,myMAC)
	publish(p3)
	p4 = receive()
	p5 = handshake.phaseThree(p4,psk,myMAC)
	publish(p5)
	p6 = receive()
	p7 = handshake.phaseFour(p6,psk,myMAC)
	publish(p7)
'''

def mq_executeHandshake(myMAC, psk):
	global expectedPhase
	expectedPhase = 1
	secret = None
	nodeID = None
	p1 = handshake.phaseOne(myMAC)

	global connection
	connection = pika.BlockingConnection(pika.ConnectionParameters(host=BROKER))
	connection.add_timeout(24,on_timeout)
	channel = connection.channel()
	result = channel.queue_declare(exclusive=True)
	queue_name = result.method.queue
	channel.queue_bind(exchange='clientHand',queue=queue_name)
	channel.basic_consume(callme,queue=queue_name,no_ack=True)
	channel.basic_publish(exchange='serverHand',routing_key='',body=p1)
	channel.start_consuming()
	print("line 98")
	channel.stop_consuming()
	connection.close()
	secret, node = handshake.getCredentials()
	return (secret,node)
	'''publish(p1)
	p2 = receive()
	p3 = handshake.phaseTwo(p2,myMAC)
	publish(p3)
	p4 = receive()
	p5 = handshake.phaseThree(p4,psk,myMAC)
	publish(p5)
	p6 = receive()
	p7 = handshake.phaseFour(p6,psk,myMAC)
	publish(p7)

	secret,nodeID = handshake.getCredentials()
	return (secret,nodeID)
'''

secret,nodeID = mq_executeHandshake(myMAC,psk)
print("My secret is: ", secret)
print("My NodeID is:", nodeID)