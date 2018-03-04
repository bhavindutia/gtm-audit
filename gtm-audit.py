'''
// Good luck with this code. Do praise if its good.
// And dont curse if its bad :)
Author: Vreddhi Bhat
Contact: vbhat@akamai.com
'''

import json
from akamai.edgegrid import EdgeGridAuth
from GTMApiWrapper import gtm
import argparse
import configparser
import requests
import os
import logging
import csv
from xlsxwriter.workbook import Workbook


#Setup logging
if not os.path.exists('logs'):
    os.makedirs('logs')
logFile = os.path.join('logs', 'GTMConfigKit_log.log')

auditLivenessFile = 'gtm-liveness-test-audit.csv'
auditPropertiesFile = 'gtm-properties-audit.csv'
auditDomainsFile = 'gtm-domains-audit.csv'
auditXLSXFile = 'gtm-audit.xlsx'

#Set the format of logging in console and file seperately
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
consoleFormatter = logging.Formatter("%(message)s")
rootLogger = logging.getLogger()


logfileHandler = logging.FileHandler(logFile, mode='w')
logfileHandler.setFormatter(logFormatter)
rootLogger.addHandler(logfileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(consoleFormatter)
rootLogger.addHandler(consoleHandler)
#Set Log Level to DEBUG, INFO, WARNING, ERROR, CRITICAL
rootLogger.setLevel(logging.INFO)

try:
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.expanduser("~"),'.edgerc'))
    client_token = config['gtm']['client_token']
    client_secret = config['gtm']['client_secret']
    access_token = config['gtm']['access_token']
    access_hostname = config['gtm']['host']
    session = requests.Session()
    session.auth = EdgeGridAuth(
    			client_token = client_token,
    			client_secret = client_secret,
    			access_token = access_token
                )
except (NameError, AttributeError, KeyError):
    rootLogger.info("\nError parsing credentials: Please check that your '~/.edgerc' file exists and contains a [gtm] section.\n")
    exit()

#Main arguments
parser = argparse.ArgumentParser()
parser.add_argument("-help",help="Use -h for detailed help options",action="store_true")
parser.add_argument("-listDomains",help="Display names of all available GTM domains in the account",action="store_true")
parser.add_argument("-generateAudit",help="Generate the GTM domain details",action="store_true")

parser.add_argument("-debug",help="DEBUG mode to generate additional logs for troubleshooting",action="store_true")

args = parser.parse_args()


if not args.listDomains and not args.generateAudit:
    rootLogger.info("Use -h for help options")
    exit()

#Override log level if user wants to run in debug mode
#Set Log Level to DEBUG, INFO, WARNING, ERROR, CRITICAL
if args.debug:
    rootLogger.setLevel(logging.DEBUG)


if args.listDomains:
    gtmObject = gtm(access_hostname)
    domainList = gtmObject.listDomains(session)
    if domainList.status_code == 200:
        for eachDomain in domainList.json()['items']:
            rootLogger.info(eachDomain['name'])
    else:
        rootLogger.info('Unable to fetch domain names')
        rootLogger.info('Reason is: ' + domainList.json()['detail'])
        exit()

if args.generateAudit:
    if not os.path.exists('output'):
        os.makedirs('output')

    # Generate Headers
    with open(os.path.join('output', auditLivenessFile),'w') as fileHandler:
        fileHandler.write('Domain Name,Property Name,Liveness Test Name,Liveness Test Protocol,Liveness Test Host Header,Liveness Test Interval,Liveness Test Object,Liveness Test TimeOut, Test Object Port, Error 3xx, Error 4xx, Error 5xx\n')

    with open(os.path.join('output', auditDomainsFile),'w') as fileHandler2:
        fileHandler2.write('Domain Name,Domain Type,Load Imbalance Factor,Property Name,Email Notification List\n')

    with open(os.path.join('output', auditPropertiesFile),'w') as fileHandler3:
        fileHandler3.write('Domain Name,Property Name,DNS TTL,Property Type,DC Weight, Servers,Handout CNAME,Backup Target\n')

    domainNames = []
    gtmObject = gtm(access_hostname)
    
    domainList = gtmObject.listDomains(session)
    if domainList.status_code == 200:
        for eachDomain in domainList.json()['items']:
            #rootLogger.info('Domain Name: ' + eachDomain['name'])
            domainNames.append(eachDomain['name'])
    else:
        rootLogger.info('Unable to get domain list')
        rootLogger.info('Reason is: ' + domainList.json()['detail'])
        exit()

    fileUpdatedWithProperties = False
    for eachDomain in domainNames:
        rootLogger.info('Fetching details for GTM Domain: ' + eachDomain)
        domainDetails = gtmObject.getDomainDetail(session, eachDomain)

        if domainDetails.status_code == 200:
            #Geting domain name to add to report
            domainName = domainDetails.json()['name']
            #rootLogger.info('Domain details are: ' + domainDetails.json())

            for eachProperty in domainDetails.json()['properties']:

                # Generate Domains audit file
                # Convert domainType to Luna names
                domainType = domainDetails.json()['type']
                if domainType == 'basic':
                     domainType = 'Performance'
                elif domainType == 'weighted':
                     domainType = 'Weighted Load Balancing'
                elif domainType == 'failover-only':
                     domainType = 'Failover'

                emailNotifList = ' '.join(domainDetails.json()['emailNotificationList'])

                with open(os.path.join('output', auditDomainsFile),'a') as fileHandler2:
                    fileHandler2.write(domainName + ',' + domainType + ',' + str(domainDetails.json()['loadImbalancePercentage']) + ',' + eachProperty['name'] + ',' + emailNotifList + '\n')


                # Generate LivenessTest audit file
                gtmLine = domainName  + ','
                gtmLine += eachProperty['name'] + ','
                headLine = gtmLine
                livenessTestCount = len(eachProperty['livenessTests'])
                counter = 0
                for eachLivenessTestDetail in eachProperty['livenessTests']:
                    counter += 1
                    #print(json.dumps(eachLivenessTestDetail,indent=4))
                    if 'name' in eachLivenessTestDetail and eachLivenessTestDetail['name'] is not None:
                        gtmLine += eachLivenessTestDetail['name']
                    gtmLine += ','
                    if 'testObjectProtocol' in eachLivenessTestDetail and eachLivenessTestDetail['testObjectProtocol'] is not None:
                        gtmLine += eachLivenessTestDetail['testObjectProtocol']
                    gtmLine += ','
                    if 'hostHeader' in eachLivenessTestDetail and eachLivenessTestDetail['hostHeader'] is not None:
                        gtmLine += eachLivenessTestDetail['hostHeader']
                    gtmLine += ','
                    if 'testInterval' in eachLivenessTestDetail and eachLivenessTestDetail['testInterval'] is not None:
                        gtmLine += str(eachLivenessTestDetail['testInterval'])
                    gtmLine += ','
                    if 'testObject' in eachLivenessTestDetail and eachLivenessTestDetail['testObject'] is not None:
                        gtmLine += eachLivenessTestDetail['testObject']
                    gtmLine += ','
                    if 'testTimeout' in eachLivenessTestDetail and eachLivenessTestDetail['testTimeout'] is not None:
                        gtmLine += str(eachLivenessTestDetail['testTimeout'])  
                    gtmLine += ','
                    if 'testObjectPort' in eachLivenessTestDetail and eachLivenessTestDetail['testObjectPort'] is not None:
                        gtmLine += str(eachLivenessTestDetail['testObjectPort'])  
                    gtmLine += ','
                    if 'httpError3xx' in eachLivenessTestDetail and eachLivenessTestDetail['httpError3xx'] is not None:
                        gtmLine += str(eachLivenessTestDetail['httpError3xx'])  
                    gtmLine += ','
                    if 'httpError4xx' in eachLivenessTestDetail and eachLivenessTestDetail['httpError4xx'] is not None:
                        gtmLine += str(eachLivenessTestDetail['httpError4xx'])  
                    gtmLine += ','
                    if 'httpError5xx' in eachLivenessTestDetail and eachLivenessTestDetail['httpError5xx'] is not None:
                        gtmLine += str(eachLivenessTestDetail['httpError5xx'])  
                    if livenessTestCount > counter:
                        #Make a new line for another Liveness Test
                        gtmLine += '\n' + headLine


                with open(os.path.join('output', auditLivenessFile),'a') as fileHandler:
                    fileHandler.write(gtmLine)
                    fileHandler.write('\n')
                    fileUpdatedWithProperties = True


                # Generate Properties audit file
                propertyType = eachProperty['type']
                propertyBackupCname = eachProperty['backupCName']
                propertyBackupIp = eachProperty['backupIp']
                propertyLine = domainName + ','
                propertyLine += eachProperty['name'] + ',' 
                propertyLine += str(eachProperty['dynamicTTL']) + ','
                propertyLine += propertyType + ',' 
                headLine2 = propertyLine

                # Count how many targets are enabled
                propTargetCount = 0
                for eachTrafficTargetsDetails in eachProperty['trafficTargets']:
                    if 'enabled' in eachTrafficTargetsDetails and eachTrafficTargetsDetails['enabled'] == True:
                        propTargetCount += 1

                counter = 0
                for eachTrafficTargetsDetails in eachProperty['trafficTargets']:
                    if 'enabled' in eachTrafficTargetsDetails and eachTrafficTargetsDetails['enabled'] == True:
                        counter += 1
                        #print(json.dumps(eachTrafficTargetsDetails,indent=4))
                        #if 'name' in eachTrafficTargetsDetails and eachTrafficTargetsDetails['name'] is not None:
                        #    propertyLine += eachTrafficTargetsDetails['name']
                        #propertyLine += ','
                        #if 'enabled' in eachTrafficTargetsDetails and eachTrafficTargetsDetails['enabled'] is not None:
                        #    propertyLine += str(eachTrafficTargetsDetails['enabled'])
                        #propertyLine += ','
                        if 'weight' in eachTrafficTargetsDetails and eachTrafficTargetsDetails['weight'] is not None:
                            if propertyType == 'cidrmapping' or propertyType == 'geographic':
                                propertyLine += 'N/A - ' + propertyType
                            else:
                                propertyLine += str(eachTrafficTargetsDetails['weight'])
                        propertyLine += ','
                        if 'servers' in eachTrafficTargetsDetails and eachTrafficTargetsDetails['servers'] is not None:
                            if propertyType == 'cidrmapping' or propertyType == 'geographic':
                                propertyLine += 'N/A - ' + propertyType
                            else:
                                for eachTargetServer in eachTrafficTargetsDetails['servers']:
                                    propertyLine += eachTargetServer + ' '
                        propertyLine += ','
                        if 'handoutCName' in eachTrafficTargetsDetails and eachTrafficTargetsDetails['handoutCName'] is not None:
                            propertyLine += eachTrafficTargetsDetails['handoutCName']
                        propertyLine += ','
                        if propertyBackupCname is not None:
                            propertyLine += propertyBackupCname
                        elif propertyBackupIp is not None:
                            propertyLine += propertyBackupIp
                        propertyLine += ','
                        if propTargetCount > counter:
                            #Make a new line for another trafficTarget
                            propertyLine += '\n' + headLine2
         
                with open(os.path.join('output', auditPropertiesFile),'a') as fileHandler3:
                    fileHandler3.write(propertyLine)
                    fileHandler3.write('\n')
                    fileUpdatedWithProperties = True

        else:
            rootLogger.info('Error in obtaining domain details')
            if domainDetails.status_code == 404:
                rootLogger.info('Couldnt find the domain')
                exit()
            rootLogger.info('Reason is: ' + domainDetails.json()['detail'])
            exit()


    # Merge CSV files into XLSX
    workbook = Workbook(os.path.join('output', auditXLSXFile))
    worksheet = workbook.add_worksheet('Domains')
    with open(os.path.join('output', auditDomainsFile), 'rt', encoding='utf8') as f:
        reader = csv.reader(f)
        for r, row in enumerate(reader):
            for c, col in enumerate(row):
                worksheet.write(r, c, col)

    worksheet = workbook.add_worksheet('Properties')
    with open(os.path.join('output', auditPropertiesFile), 'rt', encoding='utf8') as f:
        reader = csv.reader(f)
        for r, row in enumerate(reader):
            for c, col in enumerate(row):
                worksheet.write(r, c, col)

    worksheet = workbook.add_worksheet('Liveness')
    with open(os.path.join('output', auditLivenessFile), 'rt', encoding='utf8') as f:
        reader = csv.reader(f)
        for r, row in enumerate(reader):
            for c, col in enumerate(row):
                worksheet.write(r, c, col)
    workbook.close()

    if fileUpdatedWithProperties:
        rootLogger.info('Success: GTM audit file written to output/'+ auditXLSXFile)
        os.remove(os.path.join('output', auditDomainsFile))
        os.remove(os.path.join('output', auditPropertiesFile))
        os.remove(os.path.join('output', auditLivenessFile))

