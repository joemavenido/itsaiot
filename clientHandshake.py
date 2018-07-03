from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
import rsa
import binascii

secret = ''
nodeID = ''


def phaseOne(macAddr):
	print('PHASE ONE')
	header=b'\x00\x00'
	packet=header+macAddr
	return packet


def phaseTwo(packet, macAddr):
	print('PHASE TWO')
	header=b'\x00\x01'
	cookie=packet[10:]
	print('CLIENT COOKIE IS:', binascii.hexlify(cookie))
	nxtPacket = header+macAddr+cookie
	return nxtPacket

def phaseThree(packet, psk, macAddr):
	print('PHASE THREE')
	header = b'\x00\x02'
	serverPubKey=packet[10:]
	pubKey=rsa.PublicKey.load_pkcs1(serverPubKey,format='DER')
	cypherText = rsa.encrypt(psk.encode(),pubKey)
	nxtPacket = header+macAddr+cypherText
	return nxtPacket

def phaseFour(packet, psk, macAddr):
	print('PHASE FOUR')
	global secret
	global nodeID
	header = b'\x00\x03'
	aesKey = AES.new(psk.encode(),AES.MODE_ECB)
	cypher = packet[10:]
	plain = aesKey.decrypt(cypher)
	print("plain is: ",plain)
	secret = plain[:14]
	print("remaining is: ",plain[:-2])
	nodeID = plain[-2:]
	print("My Secret is: ", secret, " and my Node ID is: ", nodeID)	
	newAES = AES.new(pad(secret,16),AES.MODE_ECB)
	print("AES key is:",pad(secret,16))
	cyphNode = newAES.encrypt(pad(nodeID,16))

	print("decrypted is ",newAES.decrypt(cyphNode))
	print("CYPHERNODE ", cyphNode)
	nxtPacket = header+macAddr+cyphNode
	return nxtPacket

def getCredentials():
	global secret
	global nodeID

	return secret, nodeID