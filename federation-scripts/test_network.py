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


class TestNetwork:

	def __init__(self):
		'''__init__ Constructor'''

		config = None

		with open('config/testeNetworkConfig.json') as data_file:
			config = json.load(data_file)
	    	

		self.computerConfig = config["computerConfig"]
		self.networkConfig = config["networkConfig"]
		self.sshTimeout = config["sshTimeout"]
		self.managerLocation = config["managerLocation"]
		
		self.fogbowApi = FogbowApi()
		pass



	def handlerErrorCreateOrder(self, msg, managerLocation):
		print("handle Error not done yet")
		# name = "Incident in create orders."
		# logger.error("Error while creating orders.")
		# createCachetIncident(name, msg, managerLocation, 1)


	def garbageCollector(self):
		print("Garbage colector not done yet")


	def createNetworkOrder(self):

		print("Creating network order")

		try:

			# Default values
			cidr = "10.10.10.0/24"
			gateway = "10.10.10.1"
			allocation = "dynamic"
					
					
			if self.networkConfig["cidr"] is not None:
				cidr = self.networkConfig["cidr"]
			if self.networkConfig["gateway"] is not None:
				gateway = self.networkConfig["gateway"]
			if self.networkConfig["allocation"] is not None:
				allocation = self.networkConfig["allocation"]
			

			logger.debug("Creating network order with the following parameters:\nCidr: %s\n\Gateway: %s\nAllocation: %s" % (cidr, gateway, allocation))

			requirements =  'Glue2CloudComputeManagerID==\"%s\"' % (self.managerLocation)
			extraParams = ["--requirements", requirements, "--cidr", cidr, "--allocation", allocation, "--gateway", gateway]
			ordersID = self.fogbowApi.createNetworkOrder(extraParams)

			if len(ordersID) > 0:
				return ordersID[0]
				
			return None

		except Exception as e:
		    logging.exception("Error while create component.")
		    return None

	def getResourceID(self, orderId):

		print("Getting resource id from order [%s]" % (orderId))
		networkId = None
		orderStatus = ""
		orderDetails = ""
		triesCount = 0

		#Waiting for order to get fulfilled
		while(triesCount <= 10):
			++triesCount
			orderDetails = self.fogbowApi.getOrder(orderId)
			orderStatus = self.fogbowApi.getOrderStatus(orderDetails)
			orderStatus = orderStatus.strip()
			
			if str(orderStatus) == "fulfilled":
				break
			else:
				time.sleep(30)


		if str(orderStatus) != "fulfilled":
			raise Exception('Timeout waiting for Order to get fulfilled') 
		
		#Waiting for order to have a networkID
		triesCount = 0
		while (triesCount <= 10):
			++triesCount
			orderDetails = self.fogbowApi.getOrder(orderId)
			networkId = self.fogbowApi.getReourcesId(orderDetails)
			
			if networkId is not None:
				break
			else:
				time.sleep(30)

		if networkId is None:
			raise Exception('Timeout waiting for resource ID') 
		else:
			return networkId


	def createComputeOrders(self, networkId):

		print("Creating Computer orders with network [%s]"% (networkId))

		try:
			
			# Default values
			orderNumber = 2
			image = "fogbow-ubuntu"
			cpuSize = 1
			memorySize = 1024
			

			# if self.computerConfig['orderNumber'] is not None:
			# 	orderNumber = self.computerConfig['orderNumber']
			if self.computerConfig['image'] is not None:
				image = self.computerConfig['image']
			if self.computerConfig['cpuSize'] is not None:
				cpuSize = self.computerConfig['cpuSize']
			if self.computerConfig['memorySize'] is not None:
				memorySize = self.computerConfig['memorySize']


			if self.managerLocation is None:
				print("no manager location")
				#TODO throws an error
			if self.publicKey is None:
				print("no publicKey")
				#TODO throws an error

			logger.debug("Creating %s orders with the following parameters: \nImage: %s\Cpu Size: %s\nMemory: %s" % (orderNumber, image, cpuSize, memorySize))

			requirements =  "Glue2vCPU >= %s && Glue2RAM >= %s Glue2CloudComputeManagerID==\'%s\'" % (self.managerLocation, cpuSize, memorySize)

			extraParams = ["--n", orderNumber, "--requirements", requirements, "--image", image, "--public-key", self.publicKey, "--network", networkId]
			ordersID = self.fogbowApi.createIntanceOrder(extraParams)
			
			if len(ordersID) < 2:
				raise Exception('Error while creating computers to test network')
			return ordersID


		except Exception as e:
		    logging.exception("Error while creating component.")
		    return None	
		

	def testComputeConnectivity(self, instanceId):

		print("Testing connectivity for instance [%s]" % (instanceId))
		 
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
						self.failedOrders.append(instanceId)
						print("An error ocurred when tried to execute SSH Command")
						#TODO add cachet incident
					else:
						self.failedOrders.append(instanceId)
						print(str(errStr))
						#TODO add cachet incident							
				else:
					if outStr == instanceId:
						print("Success on testing Instance "+instanceId)
						return sshInfo

			except AttributeError, e:
				print(str(e))
				#TODO add cachet incident
			except:
				#TODO add cachet incident
				print(str(sys.exc_info()[0]))

		else:
			print("Process failed in get instance SSH info")
		
	def getLocalNetworkIp(self, instanceId):
		resourceDetails = self.fogbowApi.getComputer(instanceId)
		self.fogbowApi.getLocalNetworkIp(resourceDetails)

	def testeConnectionBetweenMVS(self, sshInfoVM1, ipVM2):

		print("Testing connection between [%s:%s] and [%s:22]" % (sshInfoVM1[0], sshInfoVM1[1],ipVM2))
		#TELNET_OUTPUT=`ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i $SSH_PRIVATEKEY fogbow@$VM1_PUBLIC_IP "telnet $VM2_PRIVATE_IP 22 &"`
		intanceAIp = sshInfoVM1[0]
		intanceAPort = sshInfoVM1[1]

		#print " Instance created : ID: %s - IP: %s - PORT: %s" % (instanceId, intanceIp, intancePort)

		sshCommand='ssh -o UserKnownHostsFile=/dev/null -o ConnectTimeout=%s -o StrictHostKeyChecking=no -i %s -p %s fogbow@%s telnet %s 22 &' % (self.sshTimeout, self.privKeyPath, intancePort, intanceIp, ipVM2)
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

		except AttributeError, e:
			print(str(e))
			#TODO add cachet incident
		except:
			#TODO add cachet incident
			print(str(sys.exc_info()[0]))


	#Main function
	#Parameters:
	#ORDER_REQUIREMENTS
	#MANAGER_LOCATION
	#FOGBOW_CLI_PATH
	def monitoringNetwork(self):

		print("=====================================================")
		print("Monitoring manager:  %s" % (self.managerLocation))
		print("Testing network")
		print("=====================================================")
		#TODO Call cachet create new event.
		computeA = None
		computeB = None
		networkOrderID = self.createNetworkOrder()
		networkID = self.getResourceID(networkOrderID)
		computeOrderIDs = self.createComputeOrders(networkID)
		if len(computeOrderIDs) > 1:
			
			computeA = self.getResourceID(computeOrderIDs[0])
			computeB = self.getResourceID(computeOrderIDs[1])

			sshComputeA = None
			sshComputeB = None

			if computeA is not None and computeB is not None:
				sshComputeA = self.testComputeConnectivity(computeA)
				sshComputeA = self.testComputeConnectivity(computeB)

			#If have ssh Info, both instances are responding
			if sshComputeA is not None and sshComputeB is not None:
				#Get computer b Local IP
				computeBLocalIP = self.getLocalNetworkIp(computeB)
				self.testeConnectionBetweenMVS(sshComputeA, computeBLocalIP)

		else:
			print('Was not possible to test.')


