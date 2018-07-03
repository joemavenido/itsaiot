import mq_HandshakeHub
import clientEgress
import binascii
import pika
import ReceiveV2
import threading
import time
myMAC = b'\x00\x00\x84\xef\x18\x46\x24\x2b'
psk = 'HkdW54vs4FrSUS2Y'

secret, nodeID = mq_HandshakeHub.mq_executeHandshake(myMAC,psk)
connection = None

ReceiveV2.setCreds(secret,nodeID)


def push(dest,payload):
	publish(clientEgress.clientEncapsulate(b'\x00',nodeID,dest,payload,secret))

def on_timeout():
	print('pull timed out')
	global connection
	connection.close()

def isMyPull(packet):
	dstNode = packet[3:4]
	print("DEBUG: isMyPull packet: ",binascii.hexlify(packet))
	if(packet[1:2]==b'\x02' and packet[3:4]==dstNode):
		return True
	else:
		print("DEBUG: isMyPull False: ",binascii.hexlify(packet[1:2]), " not ",binascii.hexlify(dstNode))
		return False

def pullCallback(ch, method, properties, body):
	print('PULL CALLBACK DEBUG')
	payload = ReceiveV2.Receive(body)
	#print(validPacket)
	if(payload and isMyPull(body)):
		print('pulled data is: ',int.from_bytes(payload, byteorder='big'))
		#print('pulled data is: ', bytes([payload]))
		#print("pulled Data is: ",binascii.hexlify(body))
		#do something about the reply

		ch.stop_consuming()

def recCallback(ch, method, properties, body):
	ReceiveV2.Receive(body)

def pull(dest,payload):

	global connection
	connection = pika.BlockingConnection(pika.ConnectionParameters(host=mq_HandshakeHub.BROKER))
	connection.add_timeout(24,on_timeout)
	channel = connection.channel()
	result = channel.queue_declare(exclusive=True)
	queue_name = result.method.queue
	channel.queue_bind(exchange='pullData',queue=queue_name)
	channel.basic_consume(pullCallback,queue=queue_name,no_ack=True)
	publish(clientEgress.clientEncapsulate(b'\x01',nodeID,dest,payload,secret))
	channel.start_consuming()

def publish(data):
	print("sending: :",binascii.hexlify(data))
	connection = pika.BlockingConnection(pika.ConnectionParameters(host=mq_HandshakeHub.BROKER))
	channel = connection.channel()
	channel.exchange_declare(exchange='serverHand',exchange_type='fanout')
	channel.basic_publish(exchange='serverHand',routing_key='',body=data)
	connection.close()

def recPackets():
	global connection
	connection = pika.BlockingConnection(pika.ConnectionParameters(host=mq_HandshakeHub.BROKER))
	channel = connection.channel()
	result = channel.queue_declare(exclusive=True)
	queue_name = result.method.queue
	channel.queue_bind(exchange='clientHand',queue=queue_name)
	channel.basic_consume(recCallback,queue=queue_name,no_ack=True)
	channel.start_consuming()

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

t3 = threading.Thread(target = hello)
t3.daemon = True
t3.start()

#pull(b'\x12',b'lumos')