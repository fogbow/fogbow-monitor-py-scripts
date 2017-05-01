#!/usr/bin/python
from __future__ import print_function
import sys, json, logging, time, subprocess
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# from federation-scripts.cachet.cachet import Cachet
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

		config = None

		with open('config/testeComputeConfig.json') as data_file:
			config = json.load(data_file)
	    	

		self.orderNumber = config["orderNumber"]
		self.image = config["image"]
		self.cpuSize = config["cpuSize"]
		self.memorySize = config["memorySize"]
		self.managerLocation = config["managerLocation"]
		self.publicKey = config["publicKey"]
		self.privKeyPath = config["privKeyPath"]
		self.sshTimeout = config["sshTimeout"]
		self.fogbowApi = FogbowApi()
		pass

	# def createCachetIncident(self, name, message, managerLocation, status):
		
	# 	## Create incident
	# 	endpoint = ""
	# 	token = ""
	# 	componentId ='getCachetComponentIdByManager %s %s' % (managerLocation, CONST_COMPUTE_PREFIX)
		
	# 	incident = Incident(id=componentId, name=name, message=message, status=status, visible=None, component_id=componentId, component_status=CONST_COMPONENT_MAJOR_OUTAGE)
	# 	Cachet.create_incident(endpoint, incident, token)
	# 	garbageCollector()

	def handlerErrorCreateOrder(self, msg, managerLocation):
		print("not done yet")
		# name = "Incident in create orders."
		# logger.error("Error while creating orders.")
		# createCachetIncident(name, msg, managerLocation, 1)


	def garbageCollector(self):
		if len(self.failedOrders) > 0 :
			print("Cleaning failed orders..")
			print("There is/are %s failed order(s)" % (len(self.failedOrders)))
			
			for orderId in self.failedOrders:
				orderDetails = self.fogbowApi.getOrder(orderId)
				instanceId = self.fogbowApi.getReourcesId(orderDetails)
				self.fogbowApi.deleteOrder(orderId)
				if instanceId is not None:
					self.fogbowApi.deleteComputer(instanceId)


	def createOrders(self):

		print("Creating Intance orders")

		try:

			# Default values
			orderNumber = 1
			image = "fogbow-ubuntu"
			cpuSize = 1
			memorySize = 1024
			

			if self.orderNumber is not None:
				orderNumber = self.orderNumber
			if self.image is not None:
				image = self.image
			if self.cpuSize is not None:
				cpuSize = self.cpuSize
			if self.memorySize is not None:
				memorySize = self.memorySize


			if self.managerLocation is None:
				print("no manager location")
				#TODO throws an error
			if self.publicKey is None:
				print("no publicKey")
				#TODO throws an error

			logger.debug("Creating %s orders with the following parameters: \nImage: %s\Cpu Size: %s\nMemory: %s" % (orderNumber, image, cpuSize, memorySize))

			requirements =  "\"Glue2vCPU >= %s && Glue2RAM >= %s Glue2CloudComputeManagerID==\'%s\'\"" % (self.managerLocation, cpuSize, memorySize)

			extraParams = ["--n", orderNumber, "--requirements", requirements, "--image", image, "--public-key", self.publicKey]
			ordersID = self.fogbowApi.createIntanceOrder(extraParams)

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

		print("Monitoring order status. Number of orders: "+str(len(ordersIds)))

		self.readyOrders = []
		self.failedOrders = []

		# f = open('/tmp/current_orders', 'r')
		# for line in f:
		# 	ordersIds[count] = line
		# 	++count
		
		while ((len(self.readyOrders)+len(self.failedOrders)) != len(ordersIds)):
			
			for orderId in ordersIds:
				orderDetails = self.fogbowApi.getOrder(orderId)
				status = self.fogbowApi.getOrderStatus(orderDetails)
				status = status.strip()
				print("Status of "+str(orderId)+":"+str(status)+"---")
				if str(status) == "fulfilled":
					self.readyOrders.append(orderId)

			# print("Readys: "
			# print self.readyOrders
			# print "Not Readys: "
			# print ordersIds
			# print "Timed out orders: "
			# print self.timeoutOrders
			time.sleep(10)
		
		print("All orders are fulfilled.")
		#doSomethingMonitoringStatusOrderFulfilled
		print("Finishing monitoring order status ...")



	def monitoringConnectionOrder(self):

		print("Monitoring orders with instance to get IP and try SSH connection")

		for orderId in self.readyOrders:

			instanceId = None
			triesCount = 0
			loadingChar = '.'

			while (instanceId is None and triesCount < 11):
				print(loadingChar, end='\r')
				if(len(loadingChar) == 10):
					loadingChar = '.'
				else:
					loadingChar = loadingChar+'.'
				orderDetails = self.fogbowApi.getOrder(orderId)
				instanceId = self.fogbowApi.getReourcesId(orderDetails)
				
				if instanceId is not None:
					break
				else:
					time.sleep(30)

			if instanceId is None:
				#TODO create a chachet incident for this instance. Error: timeout waiting for the intance to be created
				self.failedOrders.append(orderId)
				continue
			else:
				print("Testing Instance "+instanceId)
				computerState = ""
				computerSsh = None
				triesCount = 0
				while ( (computerState != "active" or computerSsh is None) and triesCount < 11):
					#print "Getting instance informations"
					resourceDetails = self.fogbowApi.getComputer(instanceId)
					#print "Resource details "+str(resourceDetails)
					computerState = self.fogbowApi.getComputerStatus(resourceDetails)
					#print "Resource state "+str(computerState)
					computerSsh = self.fogbowApi.getComputerSSH(resourceDetails)
					#print "Resource ssh "+str(computerSsh)
					++triesCount
					time.sleep(30)

				if computerSsh is not None:
					sshInfo = computerSsh.split(":")
					intanceIp = sshInfo[0]
					intancePort = sshInfo[1]

					#print " Instance created : ID: %s - IP: %s - PORT: %s" % (instanceId, intanceIp, intancePort)

					sshCommand='ssh -o UserKnownHostsFile=/dev/null -o ConnectTimeout=%s -o StrictHostKeyChecking=no -i %s -p %s fogbow@%s echo %s' % (self.sshTimeout, self.privKeyPath, intancePort, intanceIp, orderId)
					print("executing "+sshCommand)
					out, err = subprocess.Popen(sshCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()

					try:
						
						outStr = str(out).strip()
						errStr = str(err).strip()
						print("Out process returned "+str(outStr))
						print("Err process returned "+str(errStr))

						if not outStr:
							if not errStr:
								self.failedOrders.append(orderId)
								print("An error ocurred when tried to execute SSH Command")
								#TODO add cachet incident
							else:
								self.failedOrders.append(orderId)
								print(str(errStr))
								#TODO add cachet incident							
						else:
							if outStr == orderId:
								print("Success on testing Instance "+instanceId)
						
						self.fogbowApi.deleteOrder(orderId)
						self.fogbowApi.deleteComputer(instanceId)

					except AttributeError, e:
						print(str(e))
						#TODO add cachet incident
					except:
						#TODO add cachet incident
						print(str(sys.exc_info()[0]))

				else:
					print("Process failed in get instance SSH info")


	#Main function
	#Parameters:
	#ORDER_REQUIREMENTS
	#MANAGER_LOCATION
	#FOGBOW_CLI_PATH
	def monitoringCompute(self):

		print("=====================================================")
		print("Monitoring manager:  %s" % (self.managerLocation))
		print("Testing compute")
		print("=====================================================")
		#TODO Call cachet create new event.

		orderIDs = self.createOrders()
		self.monitoringStatusOrder(orderIDs)
		self.monitoringConnectionOrder()
		self.garbageCollector()