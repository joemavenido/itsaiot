from Crypto.Hash import MD5
import clientServ
node = None
secret = None

def setCreds(s,n):
	global secret
	global node
	node = n
	secret = s

def Receive(packet):
	print("RECEIVED PACKET: ", packet)
	print("CHECKING IF THIS IS FOR ME...")

	header = packet[0:1]

	if(header == b'\x01'):
		parsePacket = parseService(packet)
		if(parsePacket != 1 and HMACCheck(parsePacket)):
			if(parsePacket['Type'] == b'\x02'):
				return parsePacket['Payload']
			clientServ.service(parsePacket,secret)

		# if not (parsePacket == 1):
		# 	print("OMG IT'S FOR ME :>")
		# 	parsePacket['Header'] = header
		# 	check = HMACCheck(parsePacket)
		# 	return check
		# 	#if (check):
		#	return packet

def parseService(packet):
	print("RECEIVED A SERV PACKET")
	print(packet)
	servList = [b'\x00', b'\x01', b'\x02', b'\x03', b'\x04'] #possible values for service type
	servType = packet[1:2]
	parsePacket = {'Header': '', 'Type': '', 'src': '', 'dst': '', 'Payload': '', 'HMAC': ''} #dictionary contains hex values
	invalid = 0

	#If extracted service Type is valid, continue parsing
	if (servType in servList):

		srcNode = packet[2:3]
		dstNode = packet[3:4]
		#print('dstNode',dstNode)
		#print('node',node)
		if(dstNode == bytes([int(node)])):

			hmac = packet[-16:]
			payload = packet[4:-16]
			header = packet[0:1]

			parsePacket['Header'] = header
			parsePacket['Type'] = servType
			parsePacket['src'] = srcNode
			parsePacket['dst'] = dstNode
			parsePacket['Payload'] = payload
			parsePacket['HMAC'] = hmac

			return parsePacket

		else:
			invalid = 1

	else:
		invalid = 1

	if (invalid):
		return invalid

def HMACCheck(parsePacket):
	#print("HMAC CHECK")
	#print(parsePacket)
	headers = b''
	order = ['Header', 'Type', 'src', 'dst', 'Payload']
	for index in order:
		#print("concating: ",parsePacket[index])
		headers = headers + parsePacket[index]
	Hash = parsePacket['HMAC'].hex() # get bytes literally
	temp = headers + secret
	#print("HMACCheck: data is: ",headers)
	#print("HMACCheck: secret is: ",secret)
	ht = MD5.new()
	ht.update(temp)
	final = ht.hexdigest()
	#print("HASH COMPUTED: ",final)
	#print("HASH RECEIVED: ", Hash)
	#If computed hash is same with received hash, it has passsed authentication
	if Hash == final:
		print("Packet is valid")
		return True
	#Else, it has not passed authentication
	else:
		print("Packet is invalid")
		return False
