from Crypto.Hash import MD5

def clientEncapsulate(servtype,src,dest,payload,secret):
	print("clientEncapsulate: src is: ",bytes([int(src)]))
	print("clientEncapsulate: dest is: ",dest)
	header = b'\x01'+servtype+bytes([int(src)])+dest+payload
	temp = header + secret
	ht = MD5.new()
	ht.update(temp)
	final = ht.hexdigest()
	packet = header + bytes.fromhex(final)
	return packet