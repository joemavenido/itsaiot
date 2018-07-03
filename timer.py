import sqliteConnector
import time
def checkNodes():
	#print("checking nodes")
	while True:	
		time.sleep(30)
		print("checking nodes")
		nodeTimers = sqliteConnector.getTimers()
		updatedTimers = []
		for timer in nodeTimers:
			nodeID = timer[0]
			isAlive = timer[1]
			if(isAlive == 1):
				print("node ",nodeID," is alive")
				updatedTimers.append((nodeID,0))
			else:
				sqliteConnector.killNode(nodeID)
				print("node ",nodeID," is dead")
		for timer in updatedTimers:	
			sqliteConnector.updateTimer(timer[0],timer[1])