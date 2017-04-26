#!/usr/bin/python
import sys, json, logging, re, subprocess
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


class FogbowApi:

	def __init__(self, cliPath, url, authToken):
		self.cliPath = cliPath
		self.url = url
		self.authToken = authToken 

	def execute_cli_command(self, elementType, commandType, extraParams):

		cliCommand = "java -cp %s org.fogbowcloud.cli.Main %s --%s --url %s --auth-token %s %s" % (self.cliPath, elementType, commandType, self.url, self.authToken, extraParams)
		
		out, err = subprocess.Popen(cliCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell = False).communicate()

		try:
			
			outStr = str(out).strip()
			errStr = str(err).strip()
			logger.debug("Out process returned "+str(outStr))
			logger.debug("Err process returned "+str(errStr))

			if not outStr:
				if not errStr:
					logger.error("An error ocurred when tried to execute Fogbow CLI")
					return None
				else:
					logger.error(errStr)
					return None
			else:
				return outStr
				
		except AttributeError, e:
			logger.error(str(e))
		except:
			logger.error(str(sys.exc_info()[0]))

	def extractOrderIds(self, orders):

		orderIdsList=[]
		ordersIds = orders.split("\n")
		count=0
		for idDetail in ordersIds:
			idDetailList = idDetail.split("/order/")
			if len(idDetailList) > 1:
				orderIdsList[count] = idDetailList[1]
				++count

		return orderIdsList

	def getPropertyFromDetail(self, key, details):

		detailsProperties = details.split("\n")
		count=0
		for prop in OrderProperties:
			if "X-OCCI-Attribute: " in detailsProperties:
				propList = prop.split("=")
				if propList[0] == key:
					return propList[1]

		return None

	##### Functions for ORDER #####
	def createIntanceOrder(self, extraParams):
		createInstanceDetails = " --resource-kind compute %s" % (extraParams)
		orderIds = self.execute_cli_command("order","create",createInstanceDetails)
		return self.extractOrderIds(orderDetails)

	def createNetworkOrder(self, extraParams):
		createNetworkDetails = " --resource-kind network %s" % (extraParams)
		orderIds = self.execute_cli_command("order","create",createNetworkDetails)
		return self.extractOrderIds(orderDetails)

	def createStorageOrder(self, extraParams):
		createStorageDetails = " --resource-kind storage %s" % (extraParams)
		orderIds = self.execute_cli_command("order","create",createStorageDetails)
		return self.extractOrderIds(orderDetails)

	def getOrder(self, orderId):
		extraParams = "--id %s" % (orderId)
		orderDetails = execute_cli_command("order","get",extraParams)
		return self.extractOrderIds(orderDetails)
	
	def getReourcesId(self, orderDetails):
		return self.getPropertyFromDetail("X-OCCI-Attribute: org.fogbowcloud.order.instance-id", orderDetails)

	def getOrderStatus(self, orderId):
		return self.getPropertyFromDetail("X-OCCI-Attribute: org.fogbowcloud.order.state", orderDetails)

	def deleteOrder(self, orderId):
		extraParams = " --id %s" % (orderId)
		orderDetails = execute_cli_command("order","delete",extraParams)
	
	##### Functions for COMPUTER #####
	def getComputer(self, instanceId):
		extraParams = " --id %s" % (instanceId)
		instanceDetails = self.execute_cli_command("instance","get",extraParams)
		return instanceDetails

	def getComputerStatus(self, instanceDetails):
		return self.getPropertyFromDetail("X-OCCI-Attribute: occi.compute.state", instanceDetails)
	
	def getComputerSSH(self, instanceDetails):
		
		sshInfo = self.getPropertyFromDetail("org.fogbowcloud.order.ssh-public-address", instanceDetails)
		
		m = re.search('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,7})', sshInfo)
		if m is not None:
			sshDetails = details.split(":")
			json_str = "{ip:%s,port:%s}" % (sshDetails[0], sshDetails[1])
			return json.loads(json_str)
		else:
			None
		
	
	def deleteComputer(self, instanceId):
		extraParams = "--id %s" % (instanceId)
		orderDetails = self.execute_cli_command("instance","delete",extraParams)

	##### Functions for NETWORK #####
	def deleteNetwork(self, networkId):
		extraParams = " --id %s" % (networkId)
		orderDetails = self.execute_cli_command("network","delete",extraParams)

	##### Functions for STORAGE #####
	def deleteStorage(self, storageId):
		extraParams = " --id %s" % (storageId)
		orderDetails = self.execute_cli_command("storage","delete",extraParams)
		
		
	