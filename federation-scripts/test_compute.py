#!/usr/bin/python
import sys, json, logging, time, subprocess
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from federation-scripts.cachet.cachet import Cachet
from fogbow_api import FogbowApi
#sys.path.append('./cachet/')
#import Bar

import logging
logger = logging.getLogger(__name__)

CONST_COMPUTE_PREFIX="compute_"
CONST_COMPONENT_OPERATIONAL="1"
CONST_COMPONENT_MAJOR_OUTAGE="4"

class TestComputer:

	def __init__(self):
		'''__init__ Constructor'''
		pass

	def createCachetIncident(self, name, message, managerLocation, status):
		
		## Create incident
		endpoint = ""
		token = ""
		componentId ='getCachetComponentIdByManager %s %s' % (managerLocation, CONST_COMPUTE_PREFIX)
		
		incident = Incident(id=componentId, name=name, message=message, status=status, visible=None, component_id=componentId, component_status=CONST_COMPONENT_MAJOR_OUTAGE)
		Cachet.create_incident(endpoint, incident, token)
		garbageCollector()

	def handlerErrorCreateOrder(self, msg, managerLocation):
		name = "Incident in create orders."
		logger.error("Error while creating orders.")
		createCachetIncident(name, msg, managerLocation, 1)


	def garbageCollector(self):
		#read file and delete orders
		f = open('/tmp/current_orders', 'r')
		for orderId in f:
			resourceId = FogbowApi.getReourcesId(orderId)
			if resourceId != None:
				FogbowApi.deleteOrder(orderId)
				FogbowApi.deleteComputer(resourceId)


	def createOrders(self, countOrder, image,orderRequirements, managerLocation):

		logger.debug("Creating %s orders ..." % (endpoint))

		requirements = ""

		try:
			if orderRequirements is None:
				requirements = "Glue2CloudComputeManagerID==\"%s%s" % (managerLocation, "\"")
			else:
				requirements =  orderRequirements+" && Glue2CloudComputeManagerID==\"%s%s" % (managerLocation, "\"")
				
			details = " --n %s --requirements %s --image %s --public-key %s " % (countOrder, requirements, image, self.PublicKey)
			ordersID = FogbowApi.createIntanceOrder(details)

			#save ordersID on a file: /tmp/current_orders
			f = open('/tmp/current_orders', 'w')
			f.write(ordersID)

			count = 0
			for line in f:
				++count

			if count != countOrder:
				handlerErrorCreateOrder(ordersID,managerLocation)
			else:
				


		except Exception as e:
		    logging.exception("Error while create component.")
		    return None	

	

	def monitoringStatusOrder(self):

		logger.debug("Monitoring order status.")

		ordersIds = []
		count = 0
		countReadyOrders = 0

		self.readyOrders = []

		f = open('/tmp/current_orders', 'r')
		for line in f:
			ordersIds[count] = line
			++count
		
		while (len(ordersIds) > 0):
			notReady = []
			notReadyCount = 0
			for orderId in ordersIds:
				status = FogbowApi.getOrderStatus(orderId) 
				if status == "open" or status == "pending":
					notReady[notReadyCount] = orderId
					++notReadyCount
				else:
					self.readyOrders[countReadyOrders]
					++countReadyOrders

			ordersIds = notReady
		
		logger.debug("All orders are fulfilled.")
		#doSomethingMonitoringStatusOrderFulfilled
		logger.debug("Finishing monitoring order status ...")



	def monitoringConnectionOrder(self):

		logger.debug("Monitoring orders with instance to get IP and try SSH connection")
		for orderId in self.readyOrders:
			instanceId = FogbowApi.getReourcesId(orderId)
			computerState = ""
			computerSsh = None
			retryCount = 0
			#TODO count retries ???
			while (computerState != "active" and computerSsh is None):
				resourceDetails = FogbowApi.getComputer(instanceId)
				computerState = FogbowApi.getComputerStatus(resourceDetails)
				computerSsh = FogbowApi.getComputerSSH(resourceDetails)
				++retraiCount
				time.sleep(30)

			intanceIp = computerSsh["ip"]
			intancePort = computerSsh["port"]
			sshCommand='ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i %s -p %s fogbow@%s "echo %s > /tmp/%s.output; cat /tmp/%s.output"' % (privKeyPath, intancePort, intanceIp, orderId, orderId, orderId)

			out, err = subprocess.Popen(sshCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell = False).communicate()

			try:
				
				outStr = str(out).strip()
				errStr = str(err).strip()
				logger.debug("Out process returned "+str(outStr))
				logger.debug("Err process returned "+str(errStr))

				if not outStr:
					if not errStr:
						logger.error("An error ocurred when tried to execute SSH Command")
						return None
					else:
						logger.error(errStr)
						return None
				else:
					if outStr == orderId:
						logger.error("Success on testing Instance "+instanceId)
						FogbowApi.deleteOrder(orderId)
						FogbowApi.deleteComputer(instanceId)


					
			except AttributeError, e:
				logger.error(str(e))
			except:
				logger.error(str(sys.exc_info()[0]))


	#Main function
	#Parameters:
	#ORDER_REQUIREMENTS
	#MANAGER_LOCATION
	#FOGBOW_CLI_PATH
	def monitoringCompute(self, managerLocation, orderRequirements, foggbowCliPath):

		logger.debug("=====================================================")
		logger.debug("Monitoring manager:  %s" % (managerLocation))
		logger.debug("Testing compute")
		logger.debug("=====================================================")
		#TODO Call cachet create new event.

		createOrders
		monitoringStatusOrder
		monitoringConnectionOrder
		garbageCollector
	


