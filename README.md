# Description

Filelocker is a web based secure file sharing application which facilitates easy file sharing between users at an organization and promotes secure data sharing habits.

Filelocker was developed by IT Networks and Security at Purdue University for the purpose of allowing students and faculty to share files with other people both inside and outside of Purdue University. It is a temporary and secure storage system for sharing files and data. More than 20 universities worldwide are using Filelocker for HIPAA and FERPA compliant data sharing.

# Features

* Upload and share files with users at your organization.
* Request files from public users.
* Create software distribution accounts that many users can access.
* Send encrypted messages securely.
* Retrieve user information from many sources with an extensible plugin system.
* Audit user activity.
* Implements AES-256 encryption on uploaded files and messages.
* Integrates with LDAP and CAS.

# Installation

## Requirements

*   A MySQL Server (5.x+)
*   python-mysqldb
*   python-crypto
*   python-cheetah
*   python-json
*   python-sqlalchemy (0.5.8+)
*   python-twisted (You really only need zope.interface out of this, so if you find a lighter weight twisted install that has this component, please let me know)
*   python-cherrypy3 (I've been informed that in some Debian variants and in RedHat you'll need to get CherryPy3.1.2 or better installed from source)
*   -Optional, depending on config-
  *  python-ldap
  *  python-soappy

## Filelocker 2.6 Setup Instructions

1. Backup your current filelocker.conf file
2. Unzip filelocker2.6.tar.gz over your current Filelocker instance or wherever you plan to install Filelocker (ex. /usr/filelocker)
3. Copy your filelocker.conf file back to the /etc directory in the filelocker root folder (ex. /usr/filelocker/etc)
4. Add the following section to your config, substituting as appropriate for your database instance:
```
[/]
tools.SATransaction.on = True
tools.SATransaction.dburi = "mysql+mysqldb://db_user:db_password@db_host/db_name"
tools.SATransaction.echo = False
```
   AND replace the [filelocker] section with the following, substituting as necessary for environment:
```
[filelocker]
vault="/vault"
root_url="http://localhost:8080"
root_path="/usr/filelocker"
cluster_member_id=0
```
   NOTE: Cluster member ID indicates precedence of a node in becoming the master node. The lower the number, the higher priority in become the master node.

5. Run the following command (you can pass the -h flag to see command help) to back up your current Filelocker database:  
`python setup.py -u -f /backup/db_backup.xml`  
6. Run the following command to upgrade your database (or create a new working copy depending on whether you specified the same DB info in the tools.SATransaction.dburi config parameter)  
`python setup.py -r -f /backup/db_backup.xml`  
7. If you never created an admin user, it will now be necessary to have one. To set up an account (or reset it if the password is ever lost) run the following command:  
`python setup.py -a`  
NOTE: These flags are actually chainable, so if you are brave you could try to do this in one step using  
`python setup.py -u -r -a -f /backup/db_backup.xml`
8. To start Filelocker in daemonized mode, run Filelocker.py using the "-d" parameter. Running without the "-d" parameter will start Filelocker attached to the current terminal session.
9. To stop Filelocker when in daemonized mode, run Filelocker.py with the "-a stop" parameter.
10. If you store the config file somewhere other than in the local conf directory, pass the -c [configpath] option to webFilelocker2.py on startup. Ex:  
`python Filelocker.py -a start -c /etc/conf/filelocker2/filelocker.conf`

At any time, if remote authentication (via CAS, LDAP, etc) stops working, you may revert back to local authentication by pointing your web browser to 
http://$FILELOCKER_ROOT/local (where $FILELOCKER_ROOT is the URL you normally use to access Filelocker)

## Permissions

Whenever a new attribute is created, a corresponding permission is created along with it. 

If a user should be able to share files with all users who have a certain attribute, they must be granted the permission for that attribute. 

The expiration_exempt permission is also typical for file distribution purposes, as it allows users or roles with this permission to set an expiration time of null or "Never".

## Apache Proxying
    
For production uses of Filelocker 2, it's best to run it behind Apache and leave the SSL and static file serving to the Apache server, as it can do this much more efficiently than CherryPy.

The following configuration lines might be a good starting point for your Apache instance:
```
Alias /filelocker2/static "/opt/filelocker2/static"
    
ProxyPass /filelocker2/static !
ProxyPass /filelocker2 http://localhost:8083
ProxyPassReverse /filelocker2 http://localhost:8083
```
    
This is given that you've set CherryPy to listen on port 8083 (from the configuration wizard) and that you want your webserver to host Filelocker in the form of https://www.mydomain.com/filelocker2. 

CherryPy can be set up to do the SSL management on its own, but this is probably a better solution.

I would also suggest that you put firewall rules on or in front of the web server blocking access to whatever port CherryPy is listening to prevent un-encrypted connections.
