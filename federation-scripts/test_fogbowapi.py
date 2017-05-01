#!/usr/bin/python
import sys, json, logging, time, subprocess
import os.path
from fogbow_api import FogbowApi
from test_compute import TestComputer
from test_network import TestNetwork

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

#sys.path.append('./cachet/')
#import Bar


CONST_COMPUTE_PREFIX="compute_"
CONST_COMPONENT_OPERATIONAL="1"
CONST_COMPONENT_MAJOR_OUTAGE="4"

#fogbowApi = FogbowApi()
testComputer = TestComputer()
testComputer.monitoringCompute()

testNetwork = TestNetwork()
testNetwork.monitoringNetwork()
# publicKey = "/home/gustavorag/.ssh/id_rsa.pub"
# privKeyPath = "/home/gustavorag/.ssh/id_rsa"
	

# print "Creating %s orders ..." % ("1")

# requirements = ""
# orderRequirements = None


# requirements =  "\"Glue2vCPU >= 1 && Glue2RAM >= 1024 Glue2CloudComputeManagerID==\'%s\'\"" % ("lsd.manager.naf.lsd.ufcg.edu.br")
	
# #extraParams = " --n %s --requirements %s --image %s --public-key %s " % ("1",requirements, "fogbow-ubuntu", publicKey)
# extraParams = ["--n", "1", "--requirements", requirements, "--image", "fogbow-ubuntu", "--public-key", publicKey]
# ordersID = fogbowApi.createIntanceOrder(extraParams)


# print "---------------------------------------------------------------------"
# print "------- Order created: [%s] -------"%(ordersID[0])
# print "---------------------------------------------------------------------"

# instanceId = None

# while (instanceId is None):
# 	orderDetails = fogbowApi.getOrder(ordersID[0])
# 	# print "---------------------------------------------------------------------"
# 	# print "------- Order details: "
# 	# print "------- "
# 	# print "%s"%(orderDetails)
# 	# print "------- "
# 	# print "---------------------------------------------------------------------"
# 	instanceId = fogbowApi.getReourcesId(orderDetails)
	
# 	if instanceId is not None:
# 		print "---------------------------------------------------------------------"
# 		print "------- Instance ID: [%s] -------"%(instanceId)
# 		print "---------------------------------------------------------------------"
# 	else:
# 		print "------- No ID for now. Trying again. -------"
# 		time.sleep(30)


# computerState = ""
# computerSsh = None

# #TODO count retries ???
# triesCount = 0
# while ( (computerState != "active" or computerSsh is None) and triesCount < 11):
# 	print "Getting instance informations"
# 	resourceDetails = fogbowApi.getComputer(instanceId)
# 	print "Resource details "+str(resourceDetails)
# 	computerState = fogbowApi.getComputerStatus(resourceDetails)
# 	print "Resource state "+str(computerState)
# 	computerSsh = fogbowApi.getComputerSSH(resourceDetails)
# 	print "Resource ssh "+str(computerSsh)
# 	++triesCount
# 	time.sleep(30)

# if computerSsh is not None:
# 	sshInfo = computerSsh.split(":")
# 	intanceIp = sshInfo[0]
# 	intancePort = sshInfo[1]

# 	print " Instance created : ID: %s - IP: %s - PORT: %s" % (instanceId, intanceIp, intancePort)

# 	sshCommand='ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i %s -p %s fogbow@%s echo %s' % (privKeyPath, intancePort, intanceIp, ordersID[0])
# 	print "executing "+sshCommand
# 	out, err = subprocess.Popen(sshCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()

# 	try:
		
# 		outStr = str(out).strip()
# 		errStr = str(err).strip()
# 		print "Out process returned "+str(outStr)
# 		print "Err process returned "+str(errStr)

# 		if not outStr:
# 			if not errStr:
# 				print "An error ocurred when tried to execute SSH Command"
			
# 			else:
# 				print str(errStr)
				
# 		else:
# 			if outStr == ordersID[0]:
# 				print "Success on testing Instance "+instanceId
# 				fogbowApi.deleteOrder(ordersID[0])
# 				fogbowApi.deleteComputer(instanceId)


			
# 	except AttributeError, e:
# 		print str(e)
# 	except:
# 		print str(sys.exc_info()[0])

# else:
# 	print "Process failed in get instance SSH info"

