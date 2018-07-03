import time
import binascii
def newReadLine(zb, timeout=0):
	starttime = time.time()
	#print("newReadLine")
	eol = b'\r\n'
	leneol = len(eol)
	line = bytearray()
	while True:
		c = zb.read(1)
		if (c):
			line += c
			if line[-leneol:] == eol:
			#	print('eol')
				break
		currtime = time.time()
		if (currtime - starttime >= timeout and timeout != 0):
			#print("Rline timed out!!!")
			break
	return bytes(line)