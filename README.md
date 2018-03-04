# gtm-audit

Provides a way to get info about GTM properties and associated liveness test details via Open APIs and without manually having to go into the Luna Portal. 

## Local Install
* Python 3+
* pip install edgegrid-python
* pip install xlsxwriter

### Credentials
In order to use this module, you need to:
* Set up your credential files as described in the [authorization](https://developer.akamai.com/introduction/Prov_Creds.html) and [credentials](https://developer.akamai.com/introduction/Conf_Client.html) sections of the Get Started pagegetting started guide on developer.akamai.com (the developer portal).  
* When working through this process you need to give grants for the Traffic Management Configuration.  The section in your .edgerc configuration file should be called 'gtm'.

## Functionality
This program provides the following functionality:
* Displays names of all available GTM domains in the account 
* Generates audit file that lists each GTM domains, properties, and liveness test details to a .xslx file


### listDomains
List all GTM domains 

```bash
%  python gtm-audit -listDomains
```


### generateAudit
Lists each GTM domain, property, and associated liveness test details and outputs to a file.  Output will be an .xlsx file with 3 tabs with each corresponding information

```bash
%  python gtm-audit -generateAudit
```


