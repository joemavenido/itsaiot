import sqlite3
import binascii
'''
Functions include:

getNodeList() returns nodeList
getSecret(node) returns secret
getNodeID(macAddr) returns nodeID
getPSK(macAddr) returns PSK
getAddressing(node) returns dictionary
storeCookie(cookie, macAddr)
storeSecret(nodeID, secret)
setPhase (macAddr, phase)
validateCookie(cookie, macAddr) returns True or False
checkPhase(macAddr, phase) returns True or False
validatePSK(macAddr, PSK) returns True or False
checkACL(src, dst, service) returns True or False

'''


# get functions, when no entry in DB, return None(???)

dbName = 'thesDB.db'

def getNodeList():
	conn = sqlite3.connect(dbName)
	nodeList = []
	cursor = conn.execute("SELECT * from Addressing")

	for row in cursor:
	   nodeID = row[0]
	   nodeList.append(nodeID)

	conn.close()

	return nodeList


def getSecret(node):
	conn = sqlite3.connect(dbName)
	secretConn = conn.execute("SELECT * from Secret where nodeID = ?",(node,))
	secretRow = secretConn.fetchone()
	secret = secretRow[1]

	conn.close()

	return secret

def checkSecret(secret,macAddr):
	nodeID = getNodeID(macAddr)
	DBsecret = getSecret(nodeID)
	print("nodeID is: ",nodeID)
	print("DBsecret is: ",DBsecret)
	print("secret is: ",secret)
	if(DBsecret==secret):
		return True
	else:
		return False

def getNodeID(macAddr):
	conn = sqlite3.connect(dbName)
	print("getNodeID: macAddr: ",macAddr)
	nodeConn = conn.execute("SELECT * from Addressing where phyAddress = ?",(macAddr,))
	nodeRow = nodeConn.fetchone()
	print(nodeRow)
	nodeID = nodeRow[0]

	conn.close()
	print("returning: ",nodeID)
	return nodeID


def getPSK(macAddr):
	conn = sqlite3.connect(dbName)
	PSKConn = conn.execute("SELECT * from PSK where phyAddress = ?",(macAddr,))
	PSKRow = PSKConn.fetchone()
	PSK = PSKRow[1]

	conn.close()

	return PSK


def getAddressing(node):
	conn = sqlite3.connect(dbName)
	AddConn = conn.execute("SELECT * from Addressing where nodeID = ?",(node,))
	AddRow = AddConn.fetchone()
	if not (AddRow == None):
		Infra = AddRow[2]
	conn.close()

	return Infra


def storeCookie(cookie, macAddr):
	print("SC mac:",macAddr)
	conn = sqlite3.connect(dbName)
	c=conn.cursor()
	cookie=binascii.hexlify(cookie).decode()

	data = [macAddr, 0, cookie, macAddr]


	c.execute("UPDATE Phase set cookie = ? WHERE phyAddress = ?",(cookie,macAddr))
	#c.execute("INSERT INTO Phase VALUES (?,?,?)", data)

	conn.commit()

	conn.close()


def storeSecret(secret,macAddr):
	conn = sqlite3.connect(dbName)
	nodeID = getNodeID(macAddr)
	c=conn.cursor()

	c.execute("UPDATE Secret set secret = ? WHERE nodeID = ?",(secret,nodeID))

	#data = [nodeID, secret]

	#c.execute("INSERT INTO Secret VALUES (?,?)", data)

	conn.commit()

	conn.close()

# def storeSecret(nodeID, secret):
# 	conn = sqlite3.connect(dbName)
# 	c=conn.cursor()
# 	data = [nodeID, secret]
# 	c.execute("INSERT INTO Secret VALUES (?,?)", data)
# 	conn.commit()
# 	conn.close()


def setPhase (macAddr, phase):
	conn = sqlite3.connect(dbName)
	c=conn.cursor()

	c.execute("UPDATE Phase SET phaseNum = ? WHERE phyAddress = ?", (phase,macAddr))

	conn.commit()

	conn.close()

def getPhase(macAddr):
	conn = sqlite3.connect(dbName)
	c=conn.cursor()

	DBPhase = None
	PhaseConn = conn.execute("SELECT * from Phase where phyAddress = ?",(macAddr,))
	PhaseRow = PhaseConn.fetchone()
	if not (PhaseRow == None):
		DBPhase = PhaseRow[1]
		return DBPhase

	conn.close()	

def validateCookie(cookie, macAddr):
	conn = sqlite3.connect(dbName)
	DBCookie = None
	cookieConn = conn.execute("SELECT * from Phase where phyAddress = ?",(macAddr,))
	cookieRow = cookieConn.fetchone()
	if not (cookieRow == None):
		DBCookie = cookieRow[2]

	conn.close()

	if (DBCookie == cookie):
	    return True
	else:
	    return False

def checkPhase(macAddr, phase):
	print("searching: ",macAddr)
	conn = sqlite3.connect(dbName)
	DBPhase = None
	PhaseConn = conn.execute("SELECT * from Phase where phyAddress = ?",(macAddr,))
	PhaseRow = PhaseConn.fetchone()
	if not (PhaseRow == None):
		DBPhase = PhaseRow[1]

	conn.close()

	if(DBPhase==4 and phase==0):
		print("reauth")
		return True


	if (DBPhase == phase):
		print('correct phase')
		return True
	else:
		print(DBPhase,"not",phase)
		return False


def validatePSK(macAddr, PSK):
	conn = sqlite3.connect(dbName)
	DBPSK = None
	print("looking for: ",macAddr)
	PSKConn = conn.execute("SELECT * from PSK where phyAddress = ?",(macAddr,))
	PSKRow = PSKConn.fetchone()
	if not (PSKRow == None):
		DBPSK = PSKRow[1]

	conn.close()
	print("DBPSK is: ",DBPSK)
	print("PSK is: ",PSK)
	if (DBPSK == PSK):
	    return True
	else:
	    return False


def checkACL(src, dst, service):
	conn = sqlite3.connect(dbName)
	ACLConn = conn.execute("SELECT * from ACL where source =? AND destination = ? AND service = ?", (src, dst, service))
	ACLRow = ACLConn.fetchone()

	conn.close()

	if not(ACLRow == None):
	    return True
	else:
	    return False

def storeInfra(node,mac,infra):
	conn = sqlite3.connect(dbName)
	c=conn.cursor()
	infraName=''

	if(infra==1):
		infraName='802.15.4'
	if(infra==0):
		infraName='802.11'

	print('updating addr table',mac,infraName,node)

	c.execute("UPDATE Addressing SET phyAddress = ? AND Infrastructure = ? WHERE nodeID = ?", (mac,infraName,node))

	conn.commit()
	conn.close()

def getTimers():
	conn = sqlite3.connect(dbName)
	c = conn.cursor()
	c.execute("SELECT * from Timers")
	c_nodeTimers = c.fetchall()
	nodeTimers = []

	for row in c_nodeTimers:
		nodeTimers.append(row)

	conn.close()
	return nodeTimers

def addTimer(nodeID):
	conn = sqlite3.connect(dbName)
	c=conn.cursor()
	#c.execute("INSERT INTO Timers (nodeID,isAlive) VALUES (?,?)", (nodeID,1))
	c.execute("INSERT OR IGNORE INTO Timers (nodeID,isAlive) VALUES (?,?) ", (nodeID,1))
	conn.commit()
	conn.close()

def updateTimer(nodeID,isAlive):
	conn = sqlite3.connect(dbName)
	c=conn.cursor()
	print('UPDATETIMER: nodeID: ',nodeID,' isAlive: ',isAlive)
	c.execute("UPDATE Timers SET isAlive = ? WHERE nodeID = ?", (isAlive,nodeID))
	conn.commit()
	conn.close()

def getPhyAddr(nodeID):
	conn = sqlite3.connect(dbName)
	print("gettingPhyAddr of: ",nodeID)
	c = conn.execute("SELECT * from Addressing where nodeID = ?",(nodeID,))
	nodeRow = c.fetchone()
	phyAddress = nodeRow[1]
	conn.close()
	return phyAddress

def killNode(nodeID):
	conn = sqlite3.connect(dbName)
	c = conn.cursor()
	c.execute("DELETE FROM Timers WHERE nodeID = ?",(nodeID,))
	c.execute("UPDATE Secret SET secret = ? WHERE nodeID = ?",('',nodeID))
	phyAddress = getPhyAddr(nodeID)
	print("setting ",phyAddress," to 0")
	c.execute("UPDATE Phase SET phaseNum = 0 WHERE phyAddress = ?",(phyAddress,))
	conn.commit()
	conn.close()

