import sqliteConnector
import EgressMod

def Authorize(parsePacket):
	print("I AM BEING AUTHORIZED...")
	src = (parsePacket['src'])[0]
	dst = (parsePacket['dst'])[0]
	servType = parsePacket['Type']

	if(servType==b'\x05'):
		return

	if(servType == b'\x00'):
		service = "Push"
	elif(servType == b'\x01'):
		service = "PullReq"
	elif(servType == b'\x02'):
		service = "PullRep"
	elif(servType == b'\x03'):
		service = "DataSend"
	elif(servType == b'\x04'):
		service = "DataCollect"

	authorized = sqliteConnector.checkACL(src, dst, service)

	#return authorized

	if (authorized):
		print('I AM AUTHORIZED\n', parsePacket)
		EgressMod.Egress(parsePacket)
	else:
		print("UNAUTHORIZED SERVICE")
