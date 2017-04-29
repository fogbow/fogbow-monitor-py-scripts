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

	def __init__(self, orderMumber, image, cpuSize, memorySize, managerLocation, publicKey, sshTimeout):
		'''__init__ Constructor'''
		self.orderMumber = orderMumber
		self.image = image
		self.cpuSize = cpuSize
		self.memorySize = memorySize
		self.managerLocation = managerLocation
		self.publicKey = publicKey
		self.sshTimeout = sshTimeout
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
		# f = open('/tmp/current_orders', 'r')
		# for orderId in f:
		# 	resourceId = FogbowApi.getReourcesId(orderId)
		# 	if resourceId != None:
		# 		FogbowApi.deleteOrder(orderId)
		# 		FogbowApi.deleteComputer(resourceId)


	def createOrders(self):

		print "Creating Intance orders"

		try:

			orderMumber = 1
			image = "fogbow-ubuntu"
			cpuSize = 1
			memorySize = 1024
			

			if self.orderMumber is not None:
				orderMumber = self.orderMumber
			if self.image is not None:
				image = self.image
			if self.cpuSize is not None:
				cpuSize = self.cpuSize
			if self.memorySize is not None:
				memorySize = self.memorySize


			if self.managerLocation is not None:
			if self.publicKey is not None:

			logger.debug("Creating %s orders with the following parameters: \nImage: %s\Cpu Size: %s\nMemory: %s" % (orderMumber, image, cpuSize, memorySize))

			requirements =  "\"Glue2vCPU >= %s && Glue2RAM >= %s Glue2CloudComputeManagerID==\'%s\'\"" % (self.managerLocation, cpuSize, memorySize)

			extraParams = ["--n", orderMumber, "--requirements", requirements, "--image", image, "--public-key", self.publicKey]
			ordersID = fogbowApi.createIntanceOrder(extraParams)

			#save ordersID on a file: /tmp/current_orders
			# f = open('/tmp/current_orders', 'w')
			# f.write(ordersID)

			# count = 0
			# for line in f:
			# 	++count

			# if count != countOrder:
			# 	handlerErrorCreateOrder(ordersID,managerLocation)
			# else:
				
			return ordersID

		except Exception as e:
		    logging.exception("Error while create component.")
		    return None	

	

	def monitoringStatusOrder(self, ordersIds):

		print "Monitoring order status."

		count = 0
		countReadyOrders = 0

		self.readyOrders = []

		# f = open('/tmp/current_orders', 'r')
		# for line in f:
		# 	ordersIds[count] = line
		# 	++count
		
		while (len(ordersIds) > 0):
			notReady = []
			notReadyCount = 0
			for orderId in ordersIds:
				status = fogbowApi.getOrder(orderId)
				instanceId = fogbowApi.getOrderStatus(orderDetails)
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

		print "Monitoring orders with instance to get IP and try SSH connection"

		for orderId in self.readyOrders:

			instanceId = None
			triesCount = 0

			while (instanceId is None and triesCount < 11):
				
				orderDetails = fogbowApi.getOrder(orderId)
				instanceId = fogbowApi.getReourcesId(orderDetails)
				
				if instanceId is not None:
					
				else:
					time.sleep(30)

			if instanceId is None:
				#TODO create a chachet incident for this instance. Error: timeout waiting for the intance to be created
				continue
			else:

				computerState = ""
				computerSsh = None
				triesCount = 0
				while ( (computerState != "active" or computerSsh is None) and triesCount < 11):
					#print "Getting instance informations"
					resourceDetails = fogbowApi.getComputer(instanceId)
					#print "Resource details "+str(resourceDetails)
					computerState = fogbowApi.getComputerStatus(resourceDetails)
					#print "Resource state "+str(computerState)
					computerSsh = fogbowApi.getComputerSSH(resourceDetails)
					#print "Resource ssh "+str(computerSsh)
					++triesCount
					time.sleep(30)

				if computerSsh is not None:
					sshInfo = computerSsh.split(":")
					intanceIp = sshInfo[0]
					intancePort = sshInfo[1]

					#print " Instance created : ID: %s - IP: %s - PORT: %s" % (instanceId, intanceIp, intancePort)

					sshCommand='ssh -o UserKnownHostsFile=/dev/null -o ConnectTimeout=%s -o StrictHostKeyChecking=no -i %s -p %s fogbow@%s echo %s' % (self.sshTimeout, privKeyPath, intancePort, intanceIp, ordersID[0])
					print "executing "+sshCommand
					out, err = subprocess.Popen(sshCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()

					try:
						
						outStr = str(out).strip()
						errStr = str(err).strip()
						#print "Out process returned "+str(outStr)
						#print "Err process returned "+str(errStr)

						if not outStr:
							if not errStr:
								print "An error ocurred when tried to execute SSH Command"
								#TODO add cachet incident
							else:
								print str(errStr)
								#TODO add cachet incident							
						else:
							if outStr == ordersID[0]:
								print "Success on testing Instance "+instanceId
						
						fogbowApi.deleteOrder(orderId)
						fogbowApi.deleteComputer(instanceId)

					except AttributeError, e:
						print str(e)
						#TODO add cachet incident
					except:
						#TODO add cachet incident
						print str(sys.exc_info()[0])

				else:
					print "Process failed in get instance SSH info"


	#Main function
	#Parameters:
	#ORDER_REQUIREMENTS
	#MANAGER_LOCATION
	#FOGBOW_CLI_PATH
	def monitoringCompute(self):

		print "====================================================="
		print "Monitoring manager:  %s" % (self.managerLocation)
		print "Testing compute"
		print "====================================================="
		#TODO Call cachet create new event.

		orderIDs = createOrders()
		monitoringStatusOrder(orderIDs)
		monitoringConnectionOrder()
		garbageCollector()
	


