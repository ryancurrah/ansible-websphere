# README

## ibmim.py
This module installs or uninstalls IBM Installation Manager. 
#### Options
| Parameter | Required | Default | Choices | Comments |
|:---------|:--------|:---------|:---------|:---------|
| state | false | present | present, absent | present=install, absent=uninstall |
| src | true | N/A | N/A | Path to installation files for Installation Manager |
| dest | false | /opt/IBM/InstallationManager | N/A | Path to desired installation directory of Installation Manager |
| logdir | false | /var/log/IBM/InstallationManager | N/A | Path and file name of installation log file |
```
# Example:
# Install:
ibmim: state=present src=/some/dir/install/ logdir=/tmp/
# Uninstall
ibmim: state=absent src=/some/dir/install/ dest=/opt/IBM/InstallationManager
```

## ibmwas.py
This module installs or uninstalls IBM WebSphere products using Installation Manager. 
#### Options
| Parameter | Required | Default | Choices | Comments |
|:---------|:--------|:---------|:---------|:---------|
| state | false | present | present, absent | present=install,absent=uninstall |
| ibmim | false | /opt/IBM/InstallationManager | N/A | Path to installation directory of Installation Manager |
| dest | false | /opt/IBM/WebSphere | N/A | Path to destination installation directory |
| im_shared | true | N/A | N/A | Path to Installation Manager shared resources folder |
| repo | true | N/A | N/A | URL or path to the installation repository used by Installation Manager to install WebSphere products |
| offering | false | com.ibm.websphere.ND.v85 | com.ibm.websphere.ND.v85,com.ibm.websphere.IHS.v85,com.ibm.websphere.PLG.v85,com.ibm.websphere.WCT.v85,com.ibm.websphere.liberty.IBMJAVA.v70,com.ibm.websphere.liberty.v85 | Name of the offering which you want to install |
| ihs_port | false | 8080 | N/A | Port for IBM HTTP Server
| logdir | false | /var/log/IBM/WebSphere | N/A | Path of installation log file

```
# Example:
# Install:
ibmwas: state=present ibmim=/opt/IBM/InstallationManager/ dest=/usr/local/WebSphere/AppServer im_shared=/usr/local/WebSphere/IMShared repo=http://example.com/was-repo/ offering=com.ibm.websphere.ND.v85
# Uninstall:
ibmwas: state=absent ibmim=/opt/IBM/InstallationManager dest=/usr/local/WebSphere/AppServer/
```

## ibmxs.py
This module installs or uninstalls IBM eXtreme Scale products using Installation Manager. 
#### Options
| Parameter | Required | Default | Choices | Comments |
|:---------|:--------|:---------|:---------|:---------|
| state | false | present | present, absent | present=install,absent=uninstall |
| ibmim | false | /opt/IBM/InstallationManager | N/A | Path to installation directory of Installation Manager |
| dest | false | /opt/IBM/ExtremeScale | N/A | Path to destination installation directory |
| repo | true | N/A | N/A | URL or path to the installation repository used by Installation Manager to install WebSphere products |
| offering | false | com.ibm.websphere.WXS.v86 | com.ibm.websphere.WXS.v86",com.ibm.websphere.WXS.was7.v86,com.ibm.websphere.WXS.was8.v86,com.ibm.websphere.WXSCLIENT.v86,com.ibm.websphere.WXSCLIENT.was7.v86,com.ibm.websphere.WXSCLIENT.was8.v86 | Name of the offering which you want to install |

```
# Example:
# Install:
ibmxs: state=present ibmim=/opt/IBM/InstallationManager/ dest=/usr/local/WebSphere/AppServer repo=http://example.com/was-repo/ offering=com.ibm.websphere.WXS.v86_8.6.0.20121115_1943
# Uninstall:
ibmxs: state=absent ibmim=/opt/IBM/InstallationManager dest=/usr/local/WebSphere/AppServer/
```

## liberty_server.py
This module start os stops a Liberty Profile server
#### Options
| Parameter | Required | Default | Choices | Comments |
|:---------|:--------|:---------|:---------|:---------|
| state | false | started | started, stopped | N/A |
| name | true | N/A | N/A | Name of the app server |
| libertydir | true | N/A | N/A | Path to binary files of the application server |

```
# Example:
# Start:
liberty_server: state=started libertydir=/usr/local/WebSphere/Liberty/ name=my-server-01
# Stop:
liberty_server: state=stopped libertydir=/usr/local/WebSphere/Liberty/ name=my-server-01
```

## profile_dmgr.py
This module creates or removes a WebSphere Application Server Deployment Manager profile. Requires a Network Deployment installation.
#### Options
| Parameter | Required | Default | Choices | Comments |
|:---------|:--------|:---------|:---------|:---------|
| state | false | present | present,absent | present=create,absent=remove |
| wasdir | false | /opt/IBM/WebSphere | N/A | Path to installation location of WAS |
| name | true | N/A | N/A | Name of the profile |
| host_name | true | N/A | N/A | Host Name |
| node_name | true | N/A | N/A | Node name of this profile |
| cell_name | false | was_cell | N/A | Name of the cell |
| username | false | wasadmin | N/A | Administrative user name |
| password | false | wasadmin | N/A | Administrative user password |
| enable_service | false | false | N/A | Enable the profile service|
| service_username | false | N/A | N/A | Service username|

```
# Example:
# Create:
profile_dmgr: state=present wasdir=/usr/local/WebSphere/AppServer/ name=dmgr cell_name=devCell host_name=localhost node_name=devcell-dmgr username=admin password=allyourbasearebelongtous
# Remove:
profile_dmgr: state=absent wasdir=/usr/local/WebSphere/AppServer/ name=dmgr
```

## profile_liberty.py
This module creates or removes a Liberty Profile server runtime
#### Options
| Parameter | Required | Default | Choices | Comments |
|:---------|:--------|:---------|:---------|:---------|
| state | false | present | present,absent | present=create,absent=remove |
| libertydir | true | N/A | N/A | Path to install location of Liberty Profile binaries |
| name | true | N/A | N/A | Name of the server which is to be created/removed |
```
# Example:
# Create:
profile_liberty: state=present libertydir=/usr/local/WebSphere/Liberty/ name=server01
# Remove
profile_liberty: state=absent libertydir=/usr/local/WebSphere/Liberty/ name=server01
```

## profile_nodeagent.py
This module creates or removes a WebSphere Application Server Node Agent profile. Requires a Network Deployment installation.
#### Options
| Parameter | Required | Default | Choices | Comments |
|:---------|:--------|:---------|:---------|:---------|
| state | false | present | present,absent | present=create,absent=remove |
| wasdir | false | /opt/IBM/WebSphere | N/A | Path to installation location of WAS |
| name | true | N/A | N/A | Name of the profile |
| template | true | N/A | N/A | WAS template profile |
| host_name | true | N/A | N/A | Host Name |
| node_name | true | N/A | N/A | Node name of this profile |
| cell_name | False | was_cell | N/A | Name of the cell |
| username | false | wasadmin | N/A | Administrative user name of the deployment manager |
| password | true | wasadmin | N/A | Administrative user password of the deployment manager |
| dmgr_host | true | N/A | N/A | Host name of the Deployment Manager |
| dmgr_port | false | 8879 | N/A | SOAP port number of the Deployment Manager |
| federate | false | N/A | N/A | Wether the node should be federated to a cell. If true, cell name cannot be the same as the cell name of the deployment manager. |
| enable_service | false | false | N/A | Enable the profile service|
| service_username | false | N/A | N/A | Service username|

```
# Example:
# Create 
profile_nodeagent: state=present wasdir=/usr/local/WebSphere/AppServer/ name=nodeagent cell_name=devCellTmp host_name=localhost node_name=devcell-node1 username=admin password=allyourbasearebelongtous dmgr_host=localhost dmgr_port=8879 federate=true
# Remove:
profile_dmgr: state=absent wasdir=/usr/local/WebSphere/AppServer/ name=nodeagent
```
