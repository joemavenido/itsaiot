import sqliteConnector
import Authentication
import serverHandshake
import binascii
import EgressMod

def Identification(packet):
	headerList = [b'\x00', b'\x01'] #possible values for header

	#print("RECEIVED PACKET: ", packet)
	print("RECEIVED PACKET: (len:",len(binascii.hexlify(packet)),") :",binascii.hexlify(packet))
	print("IDENTIFICATION MODULE")

	header = packet[0:1]

	if (header in headerList):
		if(header == b'\x00'):
			retPack = parseHandShake(packet)
			#print("returning: ",binascii.hexlify(retPack))
			if not (type(retPack) is bool):
				if not (retPack is None):
					print("returning: ",binascii.hexlify(retPack))
					EgressMod.handEgress(retPack)
		elif(header == b'\x01'):
			parsePacket = parseService(packet)
			if not (parsePacket == 1):
				print("I HAVE A VALID SERVICE PACKET FORMAT")
				parsePacket['Header'] = header
				Authentication.Authenticate(parsePacket)

def parseHandShake(packet):
	transmitPack = serverHandshake.handshakeHub(packet)
	return transmitPack

def parseService(packet):
	print("I AM A SERVICE PACKET")
	print("parseService: raw packet",packet)
	servList = [b'\x00', b'\x01', b'\x02', b'\x03', b'\x04',b'\x05'] #possible values for service type
	servType = packet[1:2]
	parsePacket = {'Header': '', 'Type': '', 'src': '', 'dst': '', 'Payload': '', 'HMAC': ''}
	invalid = 0

	if (servType in servList):

		srcNode = packet[2:3]
		dstNode = packet[3:4]
		print("parseService: src node is: ",srcNode)
		print("parseService: dst node is: ",dstNode)
		if not (validateNode(srcNode[0])):
			srcNode = 0
			invalid = 1
			print("src node is invalid ", srcNode)
		if not (validateNode(dstNode[0])):
			dstNode = 0
			invalid =1
			print("dst node is invalid ", dstNode)

		if not (invalid):
			hmac = packet[-16:]
			payload = packet[4:-16]

			parsePacket['Type'] = servType
			parsePacket['src'] = srcNode
			parsePacket['dst'] = dstNode
			parsePacket['Payload'] = payload
			parsePacket['HMAC'] = hmac

			return parsePacket
	else:
		print("servtype is invalid ", servType)
		invalid = 1

	if(invalid):
		return invalid

	
def validateNode(nodeID):
	nodeList = sqliteConnector.getNodeList()
	print("checking :",nodeID)
	if (nodeID in nodeList):
		valid = True
	else:
		valid = False

	return valid





# import binascii
# from Crypto.Hash import MD5


# header = b'\x01\x00\x07\x2c\x04\x12\xff'
# secret = 'HkdW54vs4FrSUS2Y'
# temp = header + secret.encode()
# ht = MD5.new()
# ht.update(temp)
# final = ht.hexdigest()
# packet = header + bytes.fromhex(final)

# Identification(packet)
#packet = b'\x01\x00\x07\x2c\x04\x12\xff\xb1\xfb\xe7\xf1\xe3\x02\xf1\xb3\x13\xa3\xca\xfc\x1d\xff\x14\xfe'
#packet2 = b'\x02\x00\x07\x2c\x04\x12\xff\xb1\xfb\xe7\xf1\xe3\x02\xf1\xb3\x13\xa3\xca\xfc\x1d\xff\x14\xfe'
#Identification(packet2)



