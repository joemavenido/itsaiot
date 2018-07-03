import pika
import binascii
BROKER='localhost'

def publish(packet):
	print("(mqTranceive)sending: :",binascii.hexlify(packet))
	connection = pika.BlockingConnection(pika.ConnectionParameters(host=BROKER))
	channel = connection.channel()
	channel.exchange_declare(exchange='serverHand',exchange_type='fanout')
	channel.basic_publish(exchange='serverHand',routing_key='',body=packet)
	connection.close()