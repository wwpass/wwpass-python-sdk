# WWPass Python SDK
Version 3.0
March 2014
 
## CHAPTER 1 - OVERVIEW
### Introduction
The *WWPass Python SDK* comprises a library, examples and documentation that is installed on a Service Provider's system to allow authentication using the WWPass system.  The WWPass Authentication Service is an alternative to, or replacement for, other authentication methods such as user name/password.

The sections that follow describe language-specific API calls associated with the WWPass Authentication Service.  Each reference will describe the declaration of the API, the parameters required and their meaning, followed by the expected return value(s) and raised exceptions, if any.  

The **WWPass PassKey** or **WWPass PassKey Lite** is a requirement for user authentication. 
**PassKey** is a hardware device that enables authentication and access for a given user.  A major component of the WWPass authentication capability is the software that supports the PassKey itself. Without this software, requests to an end user to authenticate their identity will fail since this software is used to directly access information stored on the PassKey and communicate with WWPass. To allow Administrator testing of the authentication infrastructure, this client software and an accompanying PassKey is required. 
**PassKey Lite** is an application for Android and iOS smartphones and tablets. The application is used to scan QR codes to authenticate into WWPass-enabled sites. Alternatively, when browsing with these mobile devices, you can tap the QR code image to authenticate into the site to access protected information directly on your phone or tablet. 
For more information about how to obtain a PassKey and register it, please refer to the WWPass web site (<http://www.wwpass.com>)  

### Licensing
The *WWPass Python SDK* is licensed under the Apache 2.0 license.  This license applies to all source code, code examples and accompanying documentation contained herein.  You can modify and re-distribute the code with the appropriate attribution.  This software is subject to change without notice and should not be construed as a commitment by WWPass.

You may obtain a copy of the License at <http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, the software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

### Customer Assistance
If you encounter a problem or have a question, you can contact the WWPass Service Desk as follows:
Phone - 1-888-WWPASS1 (+1-888-997-2771)
Email - <support@wwpass.com>
Online - [Support form](https://www.wwpass.com/support/)


## CHAPTER 2 - PYTHON PACKAGE
### About the WWPass Python Authentication Library
The Python library consists of a single file, wwpass.py.  There are two classes:

 - WWPassConnection
 - WWPassConnectionMT

Both classes have the same interface.  MT stands for Multi-Threaded; it should be used if several threads will access the same instance of the class.  WWPassConnectionMT allocates a pool of connections to the SPFE.  The pool will grow on demand.

The WWPass Python library depends on the Python cURL library with SSL support.

#### Class WWPassConnection
##### Declaration
    WWPASSConnection(key_file, cert_file, timeout=10, spfe_addr='https://spfe.wwpass.com', cafile=None)
##### Purpose
*WWPassConnection* is the class for a WWPass SPFE connection, and a new connection is initiated every time a connection request is made.  The WWPass CA certificate is required for validating the SPFE certificate and can be downloaded at <https://developers.wwpass.com/downloads/wwpass.ca>
##### Parameters
| Name | Description |
| --------- | ---------------- | 
| key_file | The path to the Service Provider's private key file. |
| cert_file | The path to the Service Provider's certificate file. |
| timeout | Timeout measured in seconds. It is used in all operations. The default is 10 seconds. |
| spfe_addr | The hostname or base URL of the SPFE. The default name is <https://spfe.wwpass.com>. |
| cafile |The path to the WWPass Service Provider CA certificate (optional). |
##### Exception (Throw)
*WWPassException* is thrown.
 
#### Class WWPassConnectionMT
##### Declaration
    WWPASSConnectionMT(key_file, cert_file, timeout=10, spfe_addr='https://spfe.wwpass.com', ca_file=None, initial_connections=2)
##### Purpose
*WWPassConnectionMT* is an extension over the WWPassConnection class to support multi-threaded applications. The actual number of connections grows on demand. This class is thread-safe.
##### Parameters
| Name | Description |
| ------- | -------------- |
| keyFile | The path to the Service Provider's private key file. |
| certFile | The path to the Service Provider's certificate file. |
| timeout | Timeout measured in seconds. It is used in all operations. The default is 10 seconds. | 
| spfeAddr | The hostname or base URL of the SPFE. The default name is <https://spfe.wwpass.com>. |
| ca_file | The path to the WWPass Service Provider CA certificate (optional). | 
| initial_connections | The number of connections to the SPFE that are initially set up. The default is 2. |
##### Exception (Throw)
*WWPassException* is thrown.

### Functions 
The following functions operate the same way for both classes, *WWPassConnection* and *WWPassConnectionMT*.  All functions return a tuple (success, data). If an operation was successful, a tuple is `(True, <return value>)`. If an error has occurred, a `(False, <error message>)` tuple is returned.

#### getName()
##### Declaration
    WWPASSConnection.getName()
##### Purpose
Calls to this function get the SP name on the certificate which was used for initiate this *WWPassConnection* instance.
##### Returns
`(True, <SP name>)` or
`(False, <error message>)`

#### getTicket()
##### Declaration
    WWPassConnection.getTicket(ttl=None, auth_types = '')
##### Purpose
Calls to this function get a newly-issued ticket from SPFE.
##### Parameters
| Name | Description |
| ------- | -------------- |
| ttl |The period in seconds for the ticket to remain valid since issuance. |
| auth_types | Defines which credentials will be asked of the user to authenticate this ticket. The values may be any combination of following letters: ‘p’ — to ask for PassKey and access code; ‘s’ — to generate cryptographically secure random number that would be available both to client and Service Provider; or empty string to ask for PassKey only (default). |
##### Returns
`(True, <Ticket issued by the SPFE>)` or
`(False, <error message>)`

#### getPUID()
#### Declaration
    WWPASSConnection.getPUID(ticket, auth_types='', finalize=None)
##### Purpose
*WWPassConnection.getPUID* gets the id of the user from the Service Provider Front End. This ID is unique for each Service Provider.
##### Parameters
| Name | Description |
| ------- | -------------- |
| ticket | The authenticated ticket. |
| auth_types | Defines which credentials will be asked of the user to authenticate this ticket. The values may be any combination of following letters: ‘p’ — to ask for PassKey and access code; ‘s’ — to generate cryptographically secure random number that would be available both to client and Service Provider; or empty string to ask for PassKey only (default). |
|finalize | Set to True value to close the ticket after this operation is finished. |
##### Returns
`(True, <PUID>)` or
`(False, <error message>)`

#### putTicket()
##### Declaration
    WWPassConnection.putTicket(ticket, ttl=None, auth_types = '')
##### Purpose
A call to this function checks the authentication of the ticket and may issue a new ticket from SPFE.  All subsequent operations should use a returned ticket instead of one provided to *putTicket*.
##### Parameters
| Name | Description |
| ------- | -------------- |
| ticket | The ticket to validate. |
| ttl | The period in seconds for the ticket to remain valid since issuance. |
| auth_types | Defines which credentials will be asked of the user to authenticate this ticket. The values may be any combination of following letters: ‘p’ — to ask for PassKey and access code; ‘s’ — to generate cryptographically secure random number that would be available both to client and Service Provider; or empty string to ask for PassKey only (default). |
##### Returns
`(True, <original or newly-issued ticket>)` or
`(False, <error message>)`

The new ticket should be used in further operations with the SPFE.  

#### readData()
##### Declaration
    WWPASSConnection.readData(ticket, container='', finalize=None)
##### Purpose
Calls to this function request data stored in the user’s data container.
##### Parameters
| Name | Description |
| ------- | -------------- |
| ticket | The authenticated ticket issued by the SPFE. |
| container | Arbitrary string (only the first 32 bytes are significant) identifying the user’s data container. |
| finalize | Set to True value to close the ticket after this operation is finished. |
##### Returns
`(True, <data>)` or 
`(True, None)` if the container was never written to, or 
`(False, <error message>)` 
 
#### readDataAndLock()
##### Declaration
    WWPASSConnection.readDataAndLock(ticket, lockTimeout, container='')
##### Purpose
Calls to this function request data stored in the user’s data container and tries to atomically lock an associated lock.
##### Parameters
| Name | Description |
| ------- | -------------- |
| ticket | The authenticated ticket issued by the SPFE. |
| lockTimeout | The period in seconds for the data container to remain protected from the new data being accessed. |
| container | Arbitrary string (only the first 32 bytes are significant) identifying the user’s data container. |
##### Returns
`(True, <data>)` or 
`(True, None)` if the container was never written to, or 
`(False, <error message>)` 

#### writeData()
##### Declaration
    WWPASSConnection.writeData(ticket, data, container='', finalize=None)
##### Purpose
Calls to this function write data into the user’s data container.
##### Parameters
| Name | Description |
| ------- | -------------- |
| ticket | The authenticated ticket issued by the SPFE. |
| data | The string to write into the container. |
| container | Arbitrary string (only the first 32 bytes are significant) identifying the user’s data container. |
| finalize | Set to True value to close the ticket after this operation is finished. |
##### Returns
`(True, None)` or
`(False, <error message>)` 

#### writeDataAndUnlock()
##### Declaration
    WWPASSConnection.writeDataAndUnlock(ticket, data, container='', finalize=None)
##### Purpose
A call to this function writes data into the user's data container and unlocks an associated lock. If the lock is already unlocked, the write will succeed, but the function will return an appropriate error.
##### Parameters
| Name | Description |
| ------- | -------------- |
| ticket | The authenticated ticket issued by the SPFE. |
| data | The string to write into the container. |
| container | Arbitrary string (only the first 32 bytes are significant) identifying the user’s data container. |
| finalize | Set to True value to close the ticket after this operation is finished. |
##### Returns
`(True, None)` or
`(False, <error message>)`

#### lock()
##### Declaration
    WWPASSConnection.lock(ticket, lockTimeout, lockid='')
##### Purpose
A call to this function tries to lock a lock identified by the user (by authenticated ticket) and lock ID.
##### Parameters
| Name | Description |
| ------- | -------------- |
| ticket | The authenticated ticket issued by the SPFE. |
| lockTimeout | The period in seconds for the data container to remain protected from the new data being accessed. |
| lockid | The arbitrary string (only the first 32 bytes are significant) identifying the lock. |
##### Returns
`(True, None)` or
`(False, <error message>)`
 
#### unlock()
##### Declaration
    WWPASSConnection.unlock(ticket, lockid='', finalize=None)
##### Purpose
A call to this function tries to unlock a lock identified by the user (by authenticated ticket) and lock ID.
##### Parameters
| Name | Description |
| ------- | -------------- |
| ticket | The authenticated ticket issued by the SPFE. |
| lockid | The arbitrary string (only the first 32 bytes are significant) identifying the lock. |
| finalize | Set to True value to close the ticket after this operation is finished. |
##### Returns
`(True, None)` or
`(False, <error message>)`
 
#### getSessionKey()
##### Declaration
    WWPASSConnection.getSessionKey(ticket, finalize=None)
##### Purpose
*WWPassConnection. getSessionKey* return cryptographically secure random number generated for the authentication transaction that is identified by ticket. This value can be used do derive cryptographic keys that will secure communication between client and Service Provider. Note that this key will be available only if the ticket was generated with 's' auth type.
##### Parameters
| Name | Description |
| ------- | -------------- |
| ticket | The authenticated ticket that was generated with 's' auth type. |
| finalize | Set to True value to close the ticket after this operation is finished. |
##### Returns
`(True, <SessionKey>)` or
`(False, <error message>)`

#### createPFID()
##### Declaration
    WWPASSConnection.createPFID(data='')
##### Purpose
A call to this function creates a new SP-only container with a unique name and returns its name.  If the data parameter is provided, it writes data to this container.  Concurrent create requests will never return the same PFID.
##### Parameters
| Name | Description |
| ------- | -------------- |
| data | The data to write to the container. |
##### Returns
`(True, <PFID of created container>)` or 
`(False, <error message>)`

#### removePFID()
##### Declaration
    WWPASSConnection.removePFID(pfid)
##### Purpose
Destroys the SP-specific data container.  The container will then become non-existent as if it were never created.
##### Parameters
| Name | Description |
| ------- | -------------- |
| pfid | The PFID of the data container to destroy. |
##### Returns
`(True, None)` or
`(False, <error message>)` 
 
#### readDataSP()
##### Declaration
    WWPASSConnection.readDataSP(pfid)
##### Purpose
Calls to this function request data stored in the SP-specific data container.
##### Parameters
| Name | Description |
| ------- | -------------- |
| pfid | The PFID of the Data Container as returned by *createPFID*. |
##### Returns
`(True, <data>)` or 
`(True, None)` if the container does not exist, or 
`(False, <error message>)`
 
#### readDataSPandLock()
##### Declaration
    WWPASSConnection.readDataSPandLock(pfid, lockTimeout)
##### Purpose
Calls to this function request the binary data stored in the Service Provider's Data Container and try to atomically lock an associated lock.
##### Parameters
| Name | Description |
| ------- | -------------- |
| pfid | The Data Container Identifier as returned by *createPFID*. |
| lockTimeout | Timeout in seconds after which the lock will expire. |
##### Returns
`(True, <data>)` or 
`(True, None)` if the container does not exist, or 
`(False, <error message>)`
 
#### writeDataSP()
##### Declaration
    WWPASSConnection.writeDataSP(pfid, data)
##### Purpose
Writes data into the SP-specific data container.
##### Parameters
| Name | Description |
| ------- | -------------- |
| pfid | The Data Container Identifier as returned by *createPFID*. |
| data | The string to write into the container. |
##### Returns
`(True, None)` or
`(False, <error message>)`  

#### writeDataSPandUnlock()
##### Declaration
    WWPASSConnection.writeDataSPandUnlock(pfid, data)
##### Purpose
Writes data into the SP-specific data container and unlocks an associated lock. If the lock is already unlocked, the write will succeed, but the function will return an appropriate error.
##### Parameters
| Name | Description |
| ------- | -------------- |
| pfid | The Data Container Identifier as returned by *createPFID*. |
| data | The string to write into the container. |
##### Returns
`(True, None)` or
`(False, <error message>)` 
 
#### lockSP()
##### Declaration
    WWPASSConnection.lockSP(lockid, lockTimeout)
##### Purpose
A call to this function tries to lock a lock identified by lockid.
##### Parameters
| Name | Description |
| ------- | -------------- |
| lockid | The arbitrary string (only the first 32 bytes are significant) identifying the lock. |
| lockTimeout | The period in seconds for the SP data to remain protected from the new data being accessed. |
##### Returns
`(True, None)` or
`(False, <error message>)` 

#### unlockSP()
##### Declaration
    WWPASSConnection.unlockSP(lockid)
##### Purpose
A call to this function tries to unlock a lock identified by lockid.
##### Parameters
| Name | Description |
| ------- | -------------- |
| lockid | The arbitrary string (only the first 32 bytes are significant) identifying the lock. |
##### Returns
`(True, None)` or
`(False, <error message>)` 

## APPENDIX A - AUTHENTICATION EXAMPLE
### Basic WWPass Authentication Example Setup

#### Preconditions
You have registered your site and have received WWPass Service Provider (SP) credentials (certificate and private key). If, for example, your site has the URL of "mysite.com" and you follow the recommended file naming convention when obtaining SP credentials, the files will be named as mysite.com.crt (for the certificate) and mysite.com.key (for the private key). The [WWPass CA certificate](https://developers.wwpass.com/downloads/wwpass.ca) should also be downloaded and made accessible to WWPass application. If you have root access to your computer, then the /etc/ssl folder is an appropriate place to store the certificates and the key.  Make sure that the script will have enough rights to read the files there. Usually access to /etc/ssl/private is quite limited.

#### Environmental Setup
##### Linux
1. Verify that you have Python Version 2.7 on your system.
2. Download the WWPass Python SDK from the WWPass Developer Site.
3. Place your SP credentials (certificate and private key) in a directory that is accessible by your Python script.

### Python Authentication Example
**Note:** The following example code intentionally lacks error checking and reporting for the sake of simplicity and clarity.  You will need to configure the following parameters in the example code Configuration Block:

 - SPNAME - Service Provider name (i.e. mycompany.com)
 - FKEY -  Absolute path to your Service Provider’s private key (i.e. /home/user/ssl/mycompany.com.key OR C:/ssl/mycompany.com.key)
 - FCERT - Absolute path to your Service Provider’s client certificate (i.e. /home/user/ssl/mycompany.com.crt OR C:/ssl/mycompany.com.crt)
 - FCA - Absolute path to the WWPass CA certificate (i.e. /home/user/ssl/wwpass_sp_ca.crt OR C:/ssl/ wwpass_sp_ca.crt)

#### Basic Authentication Example – webapp.py
In this snippet, the parameters of the code are established.  Set your own Service Provider name and paths to the certificate files. 
```
SPNAME = None
FCA = wwpass.ca.crt
```
As the server we are using creates a new thread for each request, we use *WWPassConnectionMT*.
```
conn = WWPASSConnectionMT(FKEY, FCERT, 15, 'https://spfe.wwpass.com', FCA, 0)
```
Next, if the SPNAME was not set, it will be determined automatically.
```
if not SPNAME:
 
    status, SPNAME = conn.getName()
 
    if not status:
 
        exit('Connection fail :(')
```
Next, the three templates of HTML pages are loaded.
```
# load template
HOME = open(‘templates/home.html’).read()
PUID = open(‘templates/puid.html’).read()
ERROR = open(‘templates/error.html’).read()
```
The first template (*templates/home.html*) is a login page.  This template is simply served by the *do_GET()* handler of the *HelloHandler* class.  It contains a simple JavaScript that loads the WWPass JavaScript library, starts the WWPass authentication and passes the result through a form back to the server.  Note that *SPNAME* is set by the server in this template.

The second page (*templates/puid.html*) is displayed on the form's POST request. The handler for it is a *do_POST()* function in the same class.  After parsing the query parameters, the status of the authentication is checked.  If the response code is **200 (OK)**, an authenticated ticket is extracted from the POST parameters.
```
        if 'wwpass_status' in postvars and postvars['wwpass_status'][0] == '200':
 
            # Success
            ticket = postvars['wwpass_response'][0]

```
Then, a *getPUID* is called to get a user's PUID, which is simply displayed to the user with the second page (*templates/puid.html*).  (If this had been a real application, the PUID would be used in a query to a user database.) 
```
            status, response = conn.getPUID(ticket)
```
In this snippet, the status will be True or False depending on whether or not the operation was successful.

After the PUID or an error message is received, the result is displayed to the user using the appropriate template with the second page (*templates/puid.html*) displaying the PUID in case of success, or the third page (*templates/error.html*) displaying an error message if the call failed.