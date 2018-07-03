import sqliteConnector
import Authorization
import binascii
from Crypto.Hash import MD5

def SecretQuery(node):
	secret = sqliteConnector.getSecret(node)
	return secret

def secretCheck(parsePacket): # maybe use secret query first
	secret = SecretQuery((parsePacket['src'])[0])
	headers = b'' 
	for key, value in parsePacket.items():
		if (key != 'HMAC'): # take packet except hmac
			headers = headers + value
	Hash = parsePacket['HMAC'].hex() # get bytes literally
	temp = headers + secret.encode()
	ht = MD5.new()
	ht.update(temp)
	final = ht.hexdigest()
	print("HASH COMPUTED: ",final)
	print("HASH RECEIVED: ", Hash)
	if Hash == final:
		print("Packet is valid")
		sqliteConnector.updateTimer(parsePacket['src'][0],1)
		return True		
	else:
		print("Packet is invalid")
		return False

def Authenticate(parsePacket):
	print("I AM BEING AUTHENTICATED...")
	authenticated = secretCheck(parsePacket)
	print("I AM AUTHENTICATED: ", authenticated)
#	packet = b''
	#for key,value in parsePacket.items():
#		packet = packet + value
#	return packet
	#return parsePacket

	if (authenticated):
		Authorization.Authorize(parsePacket)