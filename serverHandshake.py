from Crypto.Hash import MD5
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
import binascii
import uuid
import rsa
import pika
import time
import threading
import serial
(pubkey,privkey) = rsa.newkeys(512)
import sqliteConnector

def handshakeHub(packet):
	print("hub packet:",binascii.hexlify(packet))
	
	phase = int.from_bytes(packet[1:2],byteorder='big')
	macAddr = packet[2:10]
	macAddr = binascii.hexlify(macAddr).decode()
	
	if(sqliteConnector.checkPhase(macAddr,phase)):
		if(phase==0):
			print("PHASE ONE")
			sqliteConnector.setPhase(macAddr,phase+1)
			handPack=phaseOne(packet)
			print("handpack: ",handPack)
			return handPack
		if(phase==1):
			print("PHASE TWO")
			sqliteConnector.setPhase(macAddr,phase+1)
			handPack=phaseTwo(packet)
			print("handpack: ",handPack)
			return handPack
		if(phase==2):
			print("PHASE THREE")
			sqliteConnector.setPhase(macAddr,phase+1)
			handPack=phaseThree(packet)
			print("handpack: ",handPack)
			return handPack
			#transmit(handPack)
		if(phase==3):
			print("PHASE FOUR")
			sqliteConnector.setPhase(macAddr,phase+1)
			result=phaseFour(packet)
			if(result):
				print('AUTHENTICATION SUCCESSFUL')
			else:
				print('AUTHENTICATION FAILED')
			return result


def randGen(string_length=10):
	random = str(uuid.uuid4())
	random = random.upper()
	random = random.replace('-','')
	return random[0:string_length]

def phaseOne(packet):
	print('PHASE ONE')
	phase = packet[1:2]
	macAddr = packet[2:10]
	ht = MD5.new()
	salt = randGen(4)
	ht.update(macAddr)
	ht.update(salt.encode())
	cookie = bytes.fromhex(ht.hexdigest())
	sqliteConnector.storeCookie(cookie,binascii.hexlify(macAddr).decode())
	phaseHeaders= b'\x00\x01'
	nxtPacket = phaseHeaders+macAddr+cookie
	return nxtPacket

def phaseTwo(packet):
	global pubkey
	macAddr = packet[2:10]
	cookie = packet[-16:]

	if(sqliteConnector.validateCookie(binascii.hexlify(cookie).decode(),binascii.hexlify(macAddr).decode())):
		phaseHeader=b'\x00\x02'
		exportKey = pubkey.save_pkcs1(format='DER')
		#print("pubkey is: ",binascii.hexlify(exportKey))
		return phaseHeader+macAddr+exportKey
	else:
		sqliteConnector.setPhase(macAddr,0)
		return b'\x00\xff'+macAddr

def phaseThree(packet):
	global privkey
	phaseHeader=b'\x00\x03'
	macAddr =packet[2:10]
	cypher = packet[10:]
	decryptedKey = rsa.decrypt(cypher,privkey)
	#print("THE DECRYPTED KEY IS :",decryptedKey)
	if(sqliteConnector.validatePSK(binascii.hexlify(macAddr).decode(),decryptedKey.decode())):
		aesKey = AES.new(decryptedKey,AES.MODE_ECB)
		secret = randGen(14)
		sqliteConnector.storeSecret(secret,binascii.hexlify(macAddr).decode())
		nodeID = sqliteConnector.getNodeID(binascii.hexlify(macAddr).decode())
		print("SECRET IS: ",secret)
		print("NODEID IS: ", nodeID)
		strNodeID = str(nodeID)
		if(nodeID<10):
			strNodeID = "0"+strNodeID
		secretnode = secret+strNodeID
		cypherSecret = aesKey.encrypt(secretnode.encode())
		print("secretnode (len: ",len(secretnode.encode()),") :",secretnode.encode())
		return phaseHeader+macAddr+cypherSecret
	else:
		sqliteConnector.setPhase(macAddr,0)
		return b'\x00\xff'+macAddr

def phaseFour(packet):
	macAddr = packet[2:10]
	cypher = packet[10:]
	print("MACADDR ", macAddr)
	print("MACADDR ", binascii.hexlify(macAddr).decode())
	node = sqliteConnector.getNodeID(binascii.hexlify(macAddr).decode())
	secret = sqliteConnector.getSecret(node)
	print("secret is ",secret.encode())
	print("AES key is ",pad(secret.encode(),16))
	print("CYPHERNODE ", cypher)
	aesKey = AES.new(pad(secret.encode(),16), AES.MODE_ECB)
	plain = aesKey.decrypt(cypher)
	print("plain is: ",(plain))
	print("PLAIN IS ",plain[0:2])
	print("UNG NODE KO AY ", node, type(node))
	if(int(plain[0:2]) == node):
		sqliteConnector.addTimer(node)
		return True
	else:
		sqliteConnector.setPhase(macAddr, 0)
		return False

