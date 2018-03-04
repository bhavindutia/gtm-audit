'''
This wrapper gives does reverse look up on IP address to determine if AWS or not
Author: Bhavin Dutia
Contact: bdutia@akamai.com
'''

import argparse
import subprocess
import socket

parser = argparse.ArgumentParser()

parser.add_argument("-getIp",help="Do dig and get IP address")
parser.add_argument("-reverseLookUp",help="Get domain name based on IP")
args = parser.parse_args()

if args.getIp:

    hostname = args.getIp
    print ("Entered do Dig: ", hostname)

    #Initialize everything to boolean false
    isAws = False
    getReverseHost = 'None'
    ipAddressFromHost = 'None'

    try:
        ipAddressFromHost = socket.gethostbyname(hostname)
    except Exception:
        print ("Some exception here")

    print ("IP is ",ipAddressFromHost)

    if ipAddressFromHost:
        try :
            getReverseHost = socket.gethostbyaddr(ipAddressFromHost)

        except Exception:
            print ("Some exception here") 

        if  getReverseHost:
            if getReverseHost[0].find('amazonaws') != -1:
                isAws = True

    print ("Get Reverse Host ",getReverseHost)
    print ("Is AWS or not ",isAws)


