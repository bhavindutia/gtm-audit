'''
// Good luck with this code. Do praise if its good.
// And dont curse if its bad :)
Author: Vreddhi Bhat
Contact: vbhat@akamai.com
'''

import json


class gtm(object):
    def __init__(self,access_hostname):
        self.access_hostname = access_hostname

    def listDomains(self,session):
        """
        Function to fetch all domains

        Parameters
        -----------
        session : <string>
            An EdgeGrid Auth akamai session object

        Returns
        -------
        listDomainsRespose : cloudletGroupRespose
            (listDomainsRespose) Object with all details
        """
        listDomainsUrl = 'https://' + self.access_hostname + '/config-gtm/v1/domains/'
        listDomainsResponse = session.get(listDomainsUrl)
        return listDomainsResponse

    def getDomainDetail(self,session,domain_name):
        """
        Function to fetch details of domain

        Parameters
        -----------
        session : <string>
            An EdgeGrid Auth akamai session object

        Returns
        -------
        domainRespose : domainRespose
            (domainRespose) Object with all details
        """
        domainUrl = 'https://' + self.access_hostname + '/config-gtm/v1/domains/' + domain_name
        domainResponse = session.get(domainUrl)
        return domainResponse
