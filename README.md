# Welcome
This Splunk app was developed with one goal in mind, reduce amount of time spent validating Splunk Common Information Model (CIM) compliance of technology add-ons (TA's). Use of this app simplifies validation process in several ways:
* Identifies fields that are required, but missing
* Validates data confirms to expected CIM values
* Rapid prototyping and validation

Validation of non CIM-data models works too.  However, you will likely see *no validation regex was found* for fields that exist outside of the typical CIM field names.

This project is hosted on GitHub, https://github.com/hire-vladimir/SA-cim_vladiator

# Install
App installation is simple, and only needs to be present on the search head. Documentation around app installation can be found at http://docs.splunk.com/Documentation/AddOns/released/Overview/Singleserverinstall

# Getting Started
to fill

## Screenshot
![CIM validator](https://raw.githubusercontent.com/hire-vladimir/SA-cim_vladiator/master/static/screenshot1.png)

## System requirements
App was developed for use with Splunk 6.2+


# *mvrex* command
App ships with a custom command `mvrex`. Command allows flexibility by applying regex to MV fields, along with allowing variable/token substitution that allows for per row regex evaluation by the mean of lookups.

## Command syntax
` mvrex (<options>)?* <field> [<regex>]`

## Command arguments (optional)
Command implements arguments listed below. *field* argument is mandatory; rest are optional.

```field=<regex_string> | debug=<bool> | showunmatched=<bool> | prefix=<string> | showcount=<bool> | labelfield=<string>```

## Examples
* Command supports variable substitution, you are able to pass in new regex for each row in the dataset
```
... | eval regex="^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$" | mvrex field=mydata regex
```
* Using debug option will enable additional logging on the command to help troubleshoot command, when things go wrong
```
... | mvrex debug=1 field=mydata "^\d{1,5}$"
```
* Command support outputting counts of input, matched, and unmatched values
```
... | mvrex showcount=t showunmatched=t field=mydata "^\d{1,5}$"
```
* Command support adding a *prefix* to output fields, also custom naming of fields
```
... | mvrex prefix="myprefix" labelfield="myfieldname" "^\d{1,5}$"
```

## Troubleshooting
This command writes log data to *$SPLUNK_HOME/var/log/splunk/mvrex.log*, meaning that data is also ingested into Splunk. Magic, I know. Try searching:
```
index=_internal sourcetype=myrex
```

When debug level logging is required, pass in *debug=true* or *debug=1* argument to the command. This will display enhanced logging in Splunk UI and the log file.
```
... | mvrex debug=1 field=mydata "^\d{1,5}$"
```

# Contributors

* Lowell Alleman (Kintyre)
* araman-m

# Legal
* *Splunk* is a registered trademark of Splunk, Inc.
