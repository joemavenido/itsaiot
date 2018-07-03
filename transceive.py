import serial
import pika
from queue import Queue
import rlinetest
#BROKER = '192.168.1.100'
BROKER = 'localhost'
SERPORT = 'COM5'
connection = pika.BlockingConnection(pika.ConnectionParameters(host=BROKER))
channel = connection.channel()
packetQueue = Queue()

zb = serial.Serial(SERPORT)
channel.exchange_declare(exchange='serverHand',exchange_type='fanout')
channel.exchange_declare(exchange='clientHand',exchange_type='fanout')
channel.exchange_declare(exchange='pullData',exchange_type='fanout')
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange='serverHand',queue=queue_name)

def WF_transmit(packet):
	hType = packet[0:1]
	servType = packet[1:2]
	if(hType == b'\x01' and servType == b'\x02'):# check if pull reply
		print('sending pull data')
		channel.basic_publish(exchange='pullData',routing_key='',body=packet)
	else:
		channel.basic_publish(exchange='clientHand',
                      routing_key='',
                      body=packet)

def getZb():
	global zb
	return zb

def callback(ch, method, properties, body):
	packetQueue.put(body)

def zbTransmit(packet):
	global zb
	eol=b'\r\n'
	zb.flush()
	zb.write(packet+eol)

def zbRecv():
	global testlock
	while True:
		data = rlinetest.newReadLine(zb)
		#data = zb.readline()
		packetQueue.put(data[:-2])
		zb.flush()

def mqRecv():
	channel.basic_consume(callback,queue=queue_name,no_ack=True)
	channel.start_consuming()

def handTransmit(packet):#junk code
	global zb
	print("QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ JUNK CODE QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ")
	#zb  = serial.Serial(SERPORT)
	print("sending(len:",len(binascii.hexlify(packet)),") :",binascii.hexlify(packet))
	eol= b'\r\n'
	zb.flush()
	#time.sleep(2)
	zb.write(packet+eol)
	channel.basic_publish(exchange='clientHand',
                      routing_key='',
                      body=packet)
	