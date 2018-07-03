import threading
import sqliteConnector
import time
import binascii
def checkHandshakeThread(packet):
#	print("I AM CALLED")
	macAddr = packet[2:10]
	initPhase = sqliteConnector.getPhase(binascii.hexlify(macAddr).decode())
	time.sleep(8)
	checkPhase = sqliteConnector.getPhase(binascii.hexlify(macAddr).decode())

#	print("COMPARING : ",checkPhase,"WITH",initPhase)
	if(checkPhase != 0 and checkPhase != 4):
#		print("NOT END PHASE: ",checkPhase)
		if(initPhase==checkPhase):
			print(initPhase," is ",checkPhase)
			print("handshake expired")
			sqliteConnector.setPhase(binascii.hexlify(macAddr).decode(),0)

def checkHandshake(packet):
	t = threading.Thread(target = checkHandshakeThread,args=(packet,))
	t.daemon = True
	t.start()
