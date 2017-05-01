#!/usr/bin/python
import sys, json, logging, re, subprocess
import os.path
from pprint import pprint
currDirectory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import logging
logger = logging.getLogger("FogbowApi")

class FogbowApi:

	def __init__(self):

		config = None

		with open('config/fogbowConfi.json') as data_file:
			config = json.load(data_file)
	    	
		self.cliPath = config["cliPath"]
		self.url = config["url"]
		self.authToken = config["authToken"] 

	def execute_cli_command(self, elementType, commandType, extraParams):
		
		#args = "%s --%s --url %s --auth-token %s %s" % (elementType, commandType, self.url, self.authToken, extraParams)
		extraParams.append("--url")
		extraParams.append(self.url)
		extraParams.append("--auth-token")
		extraParams.append(self.authToken)

		cliCommand = ["java", "-cp",  self.cliPath, "org.fogbowcloud.cli.Main", elementType, "--"+commandType]
		for param in extraParams:
			cliCommand.append(param)

		out, err = subprocess.Popen(cliCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell = False).communicate()

		try:
			
			outStr = str(out).strip()
			errStr = str(err).strip()
			# logger.debug("Out process returned "+str(outStr))
			# logger.debug("Err process returned "+str(errStr))

			# print "Out process returned "+str(outStr)
			# print "Err process returned "+str(errStr)

			if not outStr:
				if not errStr:
					#logger.error("An error ocurred when tried to execute Fogbow CLI")
					print "An error ocurred when tried to execute Fogbow CLI"
					return None
				else:
					#logger.error(errStr)
					print errStr
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
		for idDetail in ordersIds:
			idDetailList = idDetail.split("/order/")
			if len(idDetailList) > 1:
				orderIdsList.append(idDetailList[1])

		return orderIdsList

	def getPropertyFromDetail(self, key, details):

		detailsProperties = details.split("\n")
		for prop in detailsProperties:
			if "X-OCCI-Attribute: " in prop:
				propList = prop.split("=")
				if propList[0] == key:
					value = propList[1]
					value = value.replace("\"", "")
					if( value == "" or value == "null"):
						return None
					else:
						return value

		return None

	##### Functions for ORDER #####
	def createIntanceOrder(self, extraParams):
		
		extraParams.append("--resource-kind")
		extraParams.append("compute")
		orderIds = self.execute_cli_command("order","create",extraParams)
		if orderIds is None:
			return None
		return self.extractOrderIds(orderIds)

	def createNetworkOrder(self, extraParams):
		
		extraParams.append("--resource-kind")
		extraParams.append("network")
		orderIds = self.execute_cli_command("order","create",extraParams)
		return self.extractOrderIds(orderIds)

	def createStorageOrder(self, extraParams):
		#createStorageDetails = " --resource-kind storage %s" % (extraParams)
		extraParams.append("--resource-kind")
		extraParams.append("storage")
		orderIds = self.execute_cli_command("order","create",extraParams)
		return self.extractOrderIds(orderIds)

	def getOrder(self, orderId):
		
		#extraParams = "--id %s" % (orderId)
		extraParams = ["--id", orderId]
		orderDetails = self.execute_cli_command("order","get",extraParams)
		return orderDetails
	
	def getReourcesId(self, orderDetails):
		return self.getPropertyFromDetail("X-OCCI-Attribute: org.fogbowcloud.order.instance-id", orderDetails)

	def getOrderStatus(self, orderDetails):
		return self.getPropertyFromDetail("X-OCCI-Attribute: org.fogbowcloud.order.state", orderDetails)

	def deleteOrder(self, orderId):
		extraParams = ["--id", orderId]
		orderDetails = self.execute_cli_command("order","delete",extraParams)
	
	##### Functions for COMPUTER #####
	def getComputer(self, instanceId):
		extraParams = ["--id", instanceId]
		instanceDetails = self.execute_cli_command("instance","get",extraParams)
		return instanceDetails

	def getComputerStatus(self, instanceDetails):
		return self.getPropertyFromDetail("X-OCCI-Attribute: occi.compute.state", instanceDetails)
	
	def getComputerSSH(self, instanceDetails):
		
		sshInfo = self.getPropertyFromDetail("X-OCCI-Attribute: org.fogbowcloud.order.ssh-public-address", instanceDetails)
		if sshInfo is not None:
			m = re.search('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,7})', sshInfo)
			if m is not None:
				return sshInfo
			else:
				None
		else:
			None
	
	def getLocalNetworkIp(self, instanceDetails):
		
		ipInfo = self.getPropertyFromDetail("X-OCCI-Attribute: org.fogbowcloud.order.local-ip-address", instanceDetails)
		if ipInfo is not None:
			m = re.search('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', ipInfo)
			if m is not None:
				return ipInfo
			else:
				None
		else:
			None
	
	def deleteComputer(self, instanceId):
		extraParams = ["--id", instanceId]
		orderDetails = self.execute_cli_command("instance","delete",extraParams)

	##### Functions for NETWORK #####
	def deleteNetwork(self, networkId):
		extraParams = ["--id", networkId]
		orderDetails = self.execute_cli_command("network","delete",extraParams)

	##### Functions for STORAGE #####
	def deleteStorage(self, storageId):
		extraParams = ["--id", storageId]
		orderDetails = self.execute_cli_command("storage","delete",extraParams)
		
		
	