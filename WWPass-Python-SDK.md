# WWPass Python SDK
Version 3.0

November 2021

## CHAPTER 1 - OVERVIEW
### Introduction
The *WWPass Python SDK* comprises a library, examples and documentation that is installed on a Service Provider's system to allow authentication using the WWPass system.  The WWPass Authentication Service is an alternative to, or replacement for, other authentication methods such as user name/password.

The sections that follow describe language-specific API calls associated with the WWPass Authentication Service.  Each reference will describe the declaration of the API, the parameters required and their meaning, followed by the expected return value(s) and raised exceptions, if any.

The **WWPass PassKey** or **WWPass PassKey Lite** is a requirement for user authentication.
**PassKey** is a hardware device that enables authentication and access for a given user.  A major component of the WWPass authentication capability is the software that supports the PassKey itself. Without this software, requests to an end user to authenticate their identity will fail since this software is used to directly access information stored on the PassKey and communicate with WWPass. To allow Administrator testing of the authentication infrastructure, this client software and an accompanying PassKey is required.
**PassKey Lite** is an application for Android and iOS smartphones and tablets. The application is used to scan QR codes to authenticate into WWPass-enabled sites. Alternatively, when browsing with these mobile devices, you can tap the QR code image to authenticate into the site to access protected information directly on your phone or tablet.
For more information about how to obtain a PassKey and register it, please refer to the WWPass web site (<https://www.wwpass.com>).

### Licensing
The *WWPass Python SDK* is licensed under the Apache 2.0 license.  This license applies to all source code, code examples and accompanying documentation contained herein.  You can modify and re-distribute the code with the appropriate attribution.  This software is subject to change without notice and should not be construed as a commitment by WWPass.

You may obtain a copy of the License at <http://www.apache.org/licenses/LICENSE-2.0>.

Unless required by applicable law or agreed to in writing, the software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

### Customer Assistance
If you encounter a problem or have a question, you can contact the WWPass Service Desk as follows:

* Phone: 1-888-WWPASS1 (+1-888-997-2771)
* Email: <support@wwpass.com>
* Online: [Support form](https://www.wwpass.com/support/)


## CHAPTER 2 - PYTHON PACKAGE
### About the WWPass Python Authentication Library
The Python library consists of a single file, `wwpass.py`.  It contains two classes:

 - `WWPassConnection`
 - `WWPassConnectionMT`

Both classes have the same interface.  MT stands for Multi-Threaded; it should be used if several threads will access the same instance of the class.  WWPassConnectionMT allocates a pool of connections to the SPFE.  The pool will grow on demand.

#### Class WWPassConnection
##### Declaration
    WWPassConnection(keyFile, certFile, timeout=10, spfeAddress='https://spfe.wwpass.com', caFile=None)
##### Purpose
`WWPassConnection` is the class for a WWPass SPFE connection, and a new connection is initiated every time a connection request is made.  The WWPass CA certificate is required for validating the SPFE certificate and can be downloaded at <https://developers.wwpass.com/downloads/wwpass.ca>.
##### Parameters
| Name | Description |
| --------- | ---------------- |
| `keyFile` | The path to the Service Provider's private key file. |
| `certFile` | The path to the Service Provider's certificate file. |
| `timeout` | Timeout of requests to SPFE measured in seconds. It is used in all operations. The default is 600 seconds. |
| `spfeAddress` | The hostname or base URL of the SPFE. The default name is <https://spfe.wwpass.com>. |
| `caFile` |The path to the WWPass Service Provider CA certificate (optional). |
##### Exception (Throw)
`WWPassException` is thrown.

#### Class WWPassConnectionMT
##### Declaration
    WWPassConnectionMT(keyFile, certFile, timeout=10, spfeAddress='https://spfe.wwpass.com', caFile=None, initialConnections=2)
##### Purpose
`WWPassConnectionMT` is an extension over the `WWPassConnection` class to support multi-threaded applications. The actual number of connections grows on demand. This class is thread-safe.
##### Parameters
| Name | Description |
| ------- | -------------- |
| `keyFile` | The path to the Service Provider's private key file. |
| `certFile` | The path to the Service Provider's certificate file. |
| `timeout` | Timeout of requests to SPFE measured in seconds. It is used in all operations. The default is 600 seconds. |
| `spfeAddress` | The hostname or base URL of the SPFE. The default name is <https://spfe.wwpass.com>. |
| `caFile` | The path to the WWPass Service Provider CA certificate (optional). |
| `initialConnections` | The number of connections to the SPFE that are initially set up. The default is 2. |
##### Throws
`WWPassException`

### Functions
The following functions operate the same way for both classes, `WWPassConnection` and `WWPassConnectionMT`.

#### getName()
##### Declaration
    WWPassConnection.getName()
##### Purpose
Calls to this function get the SP name on the certificate which was used for initiate this `WWPassConnection` instance.
##### Returns
SP name
##### Throws
`WWPassException`

#### getTicket()
##### Declaration
    WWPassConnection.getTicket(ttl=None, authTypes=())
##### Purpose
Calls to this function get a newly-issued ticket from SPFE.
##### Parameters
| Name | Description |
| ------- | -------------- |
| `ttl` | The period in seconds for the ticket to remain valid since issuance. The default is 600 seconds. |
| `authTypes` | Defines options that will be asked from the user to authenticate this ticket. This is checked against what was actually used when the ticket was authenticated. The values may be a sequence with any combination of following constants: `PIN` — to ask for PassKey and access code; `SESSION_KEY` — to generate cryptographically secure random number that would be available both to client and Service Provider; `CLIENT_KEY` — to generate cryptographic key, specific to user-applicalation pair, encrypted by one-time random key that must never leave client system; or empty sequence to ask for PassKey only (default). |
##### Returns
`{"ticket" : <Ticket issued by the SPFE>, "ttl" : <ticket's time-to-live in seconds>}`
##### Throws
`WWPassException`

#### getPUID()
#### Declaration
    WWPassConnection.getPUID(ticket, authTypes=(), finalize=None)
##### Purpose
`WWPassConnection.getPUID()` gets the id of the user from the Service Provider Front End. This ID is unique for each Service Provider.
##### Parameters
| Name | Description |
| ------- | -------------- |
| `ticket` | The authenticated ticket. |
| `authTypes` | Defines options that should have been asked from the user to authenticate this ticket. This is checked against what was actually used when the ticket was authenticated. The values may be a sequence with any combination of following constants: `PIN` — to ask for PassKey and access code; `SESSION_KEY` — to generate cryptographically secure random number that would be available both to client and Service Provider; `CLIENT_KEY` — to generate cryptographic key, specific to user-applicalation pair, encrypted by one-time random key that must never leave client system; or empty sequence to ask for PassKey only (default). |
| `finalize` | Set to `True` value to close the ticket after this operation is finished. |
##### Returns
`{"puid" : <PUID>}`
##### Throws
`WWPassException`

#### putTicket()
##### Declaration
    WWPassConnection.putTicket(ticket, ttl=None, authTypes=(), finalize=None)
##### Purpose
A call to this function checks the authentication of the ticket and may issue a new ticket from SPFE.  All subsequent operations should use a returned ticket instead of one provided to `putTicket()`.
##### Parameters
| Name | Description |
| ------- | -------------- |
| `ticket`	 | The ticket to validate. |
| `ttl` | The period in seconds for the ticket to remain valid since issuance. The default is 600 seconds. |
| `authTypes` | Defines options that should have been asked from the user to authenticate this ticket. This is checked against what was actually used when the ticket was authenticated. The values may be a sequence with any combination of following constants: `PIN` — to ask for PassKey and access code; `SESSION_KEY` — to generate cryptographically secure random number that would be available both to client and Service Provider; `CLIENT_KEY` — to generate cryptographic key, specific to user-applicalation pair, encrypted by one-time random key that must never leave client system; or empty sequence to ask for PassKey only (default). |
| `finalize` | Set to `True` value to invalidate the ticket after this operation is finished. |
##### Returns
`{"ticket" : <newly-issued ticket>, "ttl" : <ticket's time-to-live in seconds>}`
##### Throws
`WWPassException`

The new ticket should be used in further operations with the SPFE.  

#### readData()
##### Declaration
    WWPassConnection.readData(ticket, container=b'', finalize=None)
##### Purpose
Calls to this function request data stored in the user’s data container.
##### Parameters
| Name | Description |
| ------- | -------------- |
| `ticket` | The authenticated ticket issued by the SPFE. |
| `container` | Arbitrary bytes object, up to 16 bytes, identifying the user’s data container. |
| `finalize` | Set to `True` value to invalidate the ticket after this operation is finished. |
##### Returns
`{"data": <data>}` or
`{"data": None}` if the container was never written to.
##### Throws
`WWPassException`

#### readDataAndLock()
##### Declaration
    WWPassConnection.readDataAndLock(ticket, lockTimeout, container=b'')
##### Purpose
Calls to this function request data stored in the user’s data container and locks an advisory lock with the same name as the name of the data container.  Each WWPass lock has a name or “lock id.”  This function operates locks with the same name as the pertinent data container.
**Note:** The lock does not lock the data container.  It locks only itself, a common behavior to locks/flags/semaphores in other languages/APIs – so-called “advisory locks.”
##### Parameters
| Name | Description |
| ------- | -------------- |
| `ticket` | The authenticated ticket issued by the SPFE. |
| `lockTimeout` | The period in seconds for the data container to remain protected from the new lock being acquired. |
| `container` | Arbitrary bytes object, limited by 16 bytes, identifying the user’s data container. |
##### Returns
`{"data": <data>}` or
`{"data": None}` if the container was never written to.
##### Throws
`WWPassException`

#### writeData()
##### Declaration
    WWPassConnection.writeData(ticket, data, container=b'', finalize=None)
##### Purpose
Calls to this function write data into the user’s data container.
##### Parameters
| Name | Description |
| ------- | -------------- |
| `ticket` | The authenticated ticket issued by the SPFE. |
| `data` | The string to write into the container. |
| `container` | Arbitrary bytes object, limited by 16 bytes, identifying the user’s data container. |
| `finalize` | Set to `True` value to close the ticket after this operation is finished. |
##### Returns
`True`
##### Throws
`WWPassException`

#### writeDataAndUnlock()
##### Declaration
    WWPassConnection.writeDataAndUnlock(ticket, data, container=b'', finalize=None)
##### Purpose
A call to this function writes data into the user's data container and unlocks an associated lock. If the lock is already unlocked, the write will succeed, but the function will return an appropriate error.
##### Parameters
| Name | Description |
| ------- | -------------- |
| `ticket` | The authenticated ticket issued by the SPFE. |
| `data` | The string to write into the container. |
| `container` | Arbitrary bytes object, limited by 16 bytes, identifying the user’s data container. |
| `finalize` | Set to `True` value to close the ticket after this operation is finished. |
##### Returns
`True`
##### Throws
`WWPassException`

#### lock()
##### Declaration
    WWPassConnection.lock(ticket, lockTimeout, lockid)
##### Purpose
Calls to this function locks an advisory lock identified by the user (by authenticated ticket) and lock ID.
**Note:** The lock does not lock any data container.  It locks only itself, a common behavior to locks/flags/semaphores in other languages/APIs – so-called “advisory locks.”
##### Parameters
| Name | Description |
| ------- | -------------- |
| `ticket` | The authenticated ticket issued by the SPFE. |
| `lockTimeout` | The period in seconds for the data container to remain protected from the new lock being acquired. |
| `lockid` | Arbitrary bytes object, up to 16 bytes, identifying the lock. |
##### Returns
`True`
##### Throws
`WWPassException`

#### unlock()
##### Declaration
    WWPassConnection.unlock(ticket, lockid, finalize=None)
##### Purpose
Calls to this function unlocks an advisory lock identified by the user (by authenticated ticket) and lock ID.
**Note:** The lock does not lock any data container.  It locks only itself, a common behavior to locks/flags/semaphores in other languages/APIs – so-called “advisory locks.”
##### Parameters
| Name | Description |
| ------- | -------------- |
| `ticket` | The authenticated ticket issued by the SPFE. |
| `lockid` | Arbitrary bytes object, up to 16 bytes, identifying the lock. |
| `finalize` | Set to `True` value to close the ticket after this operation is finished. |
##### Returns
`True`
##### Throws
`WWPassException`

#### getSessionKey()
##### Declaration
    WWPassConnection.getSessionKey(ticket, finalize=None)
##### Purpose
`WWPassConnection.getSessionKey()` returns cryptographically secure random number generated for the authentication transaction that is identified by ticket. This value can be used do derive cryptographic keys that will secure communication between client and Service Provider. Note that this key will be available only if the ticket was generated with `SESSION_KEY` auth type.
##### Parameters
| Name | Description |
| ------- | -------------- |
| `ticket` | The authenticated ticket that was generated with `SESSION_KEY` auth type. |
| `finalize` | Set to `True` value to close the ticket after this operation is finished. |
##### Returns
`{"sessionkey" : <SessionKey>}`
##### Throws
`WWPassException`

#### getClientKey()
##### Declaration
    WWPassConnection.getClientKey(ticket)
##### Purpose
This function retrieves cryptographic key, specific to user-applicalation pair, in encrypted form. That key is encrypted by one-time random key that must never leave client system. The encrypted form, retrieved by this function can only be decrypted at the client system.
This function is only used when WWPass client-side cryptography is implemented by the application.

##### Parameters
| Name | Description |
| ------- | -------------- |
| `ticket` | The authenticated ticket that was generated with `CLIENT_KEY` auth type. |
##### Returns
`{"clientKey" : <encrypted client key>, "ttl" : <time-to-live in seconds>, "originalTicket" : <original ticket>}` or
`{"clientKey" : <encrypted client key>, "ttl" : <time-to-live in seconds>}` if the request correspond to the first issued ticket
##### Throws
    WWPassException

#### createPFID()
##### Declaration
    WWPassConnection.createPFID(data='')
##### Purpose
A call to this function creates a new SP-only container with a unique name and returns its name.  If the data parameter is provided, it writes data to this container.  Concurrent create requests will never return the same PFID.
##### Parameters
| Name | Description |
| ------- | -------------- |
| `data` | The data to write to the container. |
##### Returns
`{"pfid" : <PFID of created container>}`
##### Throws
`WWPassException`

#### removePFID()
##### Declaration
    WWPassConnection.removePFID(pfid)
##### Purpose
Destroys the SP-specific data container.  The container will then become non-existent as if it was never created.
##### Parameters
| Name | Description |
| ------- | -------------- |
| `pfid` | The PFID of the data container as returned by `createPFID()`. |
##### Returns
`True`
##### Throws
`WWPassException`

#### readDataSP()
##### Declaration
    WWPassConnection.readDataSP(pfid)
##### Purpose
Calls to this function request data stored in the SP-specific data container.
##### Parameters
| Name | Description |
| ------- | -------------- |
| `pfid` | The PFID of the Data Container as returned by `createPFID()`. |
##### Returns
`{"data" : <data>}` or
`{"data" : None}` if the container does not exist.
##### Throws
`WWPassException`

#### readDataSPandLock()
##### Declaration
    WWPassConnection.readDataSPandLock(pfid, lockTimeout)
##### Purpose
Calls to this function request the binary data stored in the Service Provider's Data Container and try to atomically lock an associated lock.
##### Parameters
| Name | Description |
| ------- | -------------- |
| `pfid` | The Data Container Identifier as returned by `createPFID()`. |
| `lockTimeout` | Timeout in seconds after which the lock will expire. |
##### Returns
`{"data" : <data>}` or
`{"data" : None}` if the container does not exist.
##### Throws
`WWPassException`

#### writeDataSP()
##### Declaration
    WWPassConnection.writeDataSP(pfid, data)
##### Purpose
Writes data into the SP-specific data container.
##### Parameters
| Name | Description |
| ------- | -------------- |
| `pfid` | The Data Container Identifier as returned by `createPFID()`. |
| `data` | The string to write into the container. |
##### Returns
`True`
##### Throws
`WWPassException`

#### writeDataSPandUnlock()
##### Declaration
    WWPassConnection.writeDataSPandUnlock(pfid, data)
##### Purpose
Writes data into the SP-specific data container and unlocks an associated lock. If the lock is already unlocked, the write will succeed, but the function will return an appropriate error.
##### Parameters
| Name | Description |
| ------- | -------------- |
| `pfid` | The Data Container Identifier as returned by `createPFID()`. |
| `data` | The string to write into the container. |
##### Returns
`True`
##### Throws
`WWPassException`

#### lockSP()
##### Declaration
    WWPassConnection.lockSP(lockid, lockTimeout)
##### Purpose
A call to this function tries to lock a lock identified by lockid.
##### Parameters
| Name | Description |
| ------- | -------------- |
| `lockid` | Arbitrary bytes object, up to 16 bytes, identifying the lock. |
| `lockTimeout` | The period in seconds for the data container to remain protected from the new lock being acquired. |
##### Returns
`True`
##### Throws
`WWPassException`

#### unlockSP()
##### Declaration
    WWPassConnection.unlockSP(lockid)
##### Purpose
A call to this function tries to unlock a lock identified by lockid.
##### Parameters
| Name | Description |
| ------- | -------------- |
| `lockid` | Arbitrary bytes object, up to 16 bytes, identifying the lock. |
##### Returns
`True`
##### Throws
`WWPassException`
