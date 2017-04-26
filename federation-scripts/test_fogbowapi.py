#!/usr/bin/python
import sys, json, logging, time
import os.path
from fogbow_api import FogbowApi

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

#sys.path.append('./cachet/')
#import Bar

import logging
logger = logging.getLogger(__name__)

CONST_COMPUTE_PREFIX="compute_"
CONST_COMPONENT_OPERATIONAL="1"
CONST_COMPONENT_MAJOR_OUTAGE="4"

cliPath = "../fogbow-components/fogbow-cli-0.0.1-SNAPSHOT-jar-with-dependencies.jar"
url = "http://10.11.4.234:8182"
fogbowApi = FogbowApi(cliPath,url,"eyJsb2duaW4iOiJmb2dib3ciLCJuYW1lIjoiRm9nYm93IFVzZXIiLCJleHBpcmF0aW9uRGF0ZSI6MTUyNDY5ODg3MTgwMH0hIyFmSXpjV1FzMjZiMkliUm5tQ1oxWk5XNnZFMnNOUmhudWhzLzZ0VEYwRFV0MVIzN0YvMmhVM0YxcDIxZEJuOXFmdWNqeFVoUG0wUGtrZE14SlFEbmcyL3lkOXN4YW8yNlp0SEczYytCRVUrdVZmelNBZThIUEwvSTVCRWRBdi8ya2d4STc4THlTQ29SREFGUFlZMVlsR3loMDYweC8rRU03QXgxSlBDRDJJdk9XOWtDS2N1RzZkcWUvSWhDb3NlL3ZUblRDMjhuN3FNU3BRRjN4WUZjS01aSFdKN3hrVlJHbHFtcGhKWDBkYzZjcFJzcldYeXlHZmR4OGYydlIzTUVOMENGUFM1S1o2NWtDaEw1QnI1MGM0cTRHQ0pZTVZ2RVZWa29qZmdQak1XMTRWMUE5Z3BwMXBvaW52NXdxMXk3amxnUGNWOUhma25TM05wdDJVZStLb0E9PQ==")

	

logger.debug("Creating %s orders ..." % ("1"))

requirements = ""
orderRequirements = None


requirements =  "\"Glue2vCPU >= 1 && Glue2RAM >= 1024 Glue2CloudComputeManagerID==\'%s\'\"" % ("lsd.manager.naf.lsd.ufcg.edu.br")
	
details = " --n %s --requirements %s --image %s --public-key %s " % ("1",requirements, "fogbow-ubuntu", "**WE#@WE")
ordersID = fogbowApi.createIntanceOrder(details)


print " Order created : "+ordersID

instanceId = None

while (instanceId is None):
	instanceId = FogbowApi.getReourcesId(orderId)
	time.sleep(30)


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

print " Instance created : ID: %s - IP: %s - PORT: %s" % (instanceId, intanceIp, intancePort)


