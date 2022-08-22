# Welcome
This Splunk app was developed with one goal in mind, reduce amount of time spent validating Splunk Common Information Model (CIM) compliance of technology add-ons (TA's). Use of this app simplifies validation process in several ways:
* Identifies fields that are required, but missing
* Validates data confirms to expected CIM values
* Rapid prototyping and validation

This project is hosted on GitHub, https://github.com/hire-vladimir/SA-cim_vladiator

# Install
## BYOL (on-prem) install
App installation is simple, and only needs to be present on the search head. Documentation around app installation can be found at http://docs.splunk.com/Documentation/AddOns/released/Overview/Singleserverinstall

## Splunk Cloud install
App installation can be completed using the self-service capabilities. Documentation around app installation can be found at https://docs.splunk.com/Documentation/SplunkCloud/latest/User/PrivateApps

# Getting Started

## Screenshot
![CIM validator](https://raw.githubusercontent.com/hire-vladimir/SA-cim_vladiator/master/static/screenshot1.png)

## System requirements
App was developed for use with Splunk 7.x+, 8.x+

# Legal
* *Splunk* is a registered trademark of Splunk, Inc.

# Updates
22-Aug-2022 - 

## Update 1

The following message appeared when installing the app in cloud env:

```
Change the version attribute in the root node of your Simple XML dashboard default/data/ui/views/cim_validator.xml to `<version=1.1>`. Earlier dashboard versions introduce security vulnerabilities into your apps and are not permitted in Splunk Cloud File: default/data/ui/views/cim_validator.xml
```

To fix add 'Version="1.1"' to the form tags in default/data/ui/views/cim_xxx files specified in the error message

## Update 2

```
The `app.conf` [package] stanza has an `id` property that does not match the uncompressed directory's name. `app.conf` [package] id: SA-cim_vladiator uncompressed directory name: SA-cim_vladiator-master. File: default/app.conf Line Number: 15
```

How to fix? I changed the app.conf to be SA-cim_validator-master

