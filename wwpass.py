# -*- coding: utf-8 -*-
__author__ = "Rostislav Kondratenko <r.kondratenko@wwpass.com>"
__date__  = "$27.11.2014 18:05:15$"

# Copyright 2009-2021 WWPASS Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pickle import loads as pickleLoads
from ssl import SSLContext, PROTOCOL_TLSv1_2
from threading import Lock
from typing import Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Iterable, List, Optional, Union # pylint: disable=unused-import, useless-suppression

import sys # pylint: disable=wrong-import-position
if sys.version_info[0] == 2:
    # Python 2
    from urllib2 import urlopen, URLError
    from urllib import urlencode
else: # Python 3
    if TYPE_CHECKING:
        from urllib.request import urlopen # pylint: disable=import-error, no-name-in-module, useless-suppression
        from urllib.parse import urlencode # pylint: disable=import-error, no-name-in-module, useless-suppression
        from urllib.error import URLError  # pylint: disable=import-error, no-name-in-module, useless-suppression
    xrange = range # pylint: disable=redefined-builtin, useless-suppression

GET = 'GET'
POST = 'POST'

SPFE_ADDRESS = 'https://spfe.wwpass.com'
DEFAULT_TIMEOUT = 10

VALID_AUTH_TYPES = 'psc' # password, sessionKey, clientKey

DEFAULT_CADATA = '''-----BEGIN CERTIFICATE-----
MIIGATCCA+mgAwIBAgIJAN7JZUlglGn4MA0GCSqGSIb3DQEBCwUAMFcxCzAJBgNV
BAYTAlVTMRswGQYDVQQKExJXV1Bhc3MgQ29ycG9yYXRpb24xKzApBgNVBAMTIldX
UGFzcyBDb3Jwb3JhdGlvbiBQcmltYXJ5IFJvb3QgQ0EwIhgPMjAxMjExMjgwOTAw
MDBaGA8yMDUyMTEyODA4NTk1OVowVzELMAkGA1UEBhMCVVMxGzAZBgNVBAoTEldX
UGFzcyBDb3Jwb3JhdGlvbjErMCkGA1UEAxMiV1dQYXNzIENvcnBvcmF0aW9uIFBy
aW1hcnkgUm9vdCBDQTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAMmF
pl1WX80osygWx4ZX8xGyYfHx8cpz29l5s/7mgQIYCrmUSLK9KtSryA0pmzrOFkyN
BuT0OU5ucCuv2WNgUriJZ78b8sekW1oXy2QXndZSs+CA+UoHFw0YqTEDO659/Tjk
NqlE5HMXdYvIb7jhcOAxC8gwAJFgAkQboaMIkuWsAnpOtKzrnkWHGz45qoyICjqz
feDcN0dh3ITMHXrYiwkVq5fGXHPbuJPbuBN+unnakbL3Ogk3yPnEcm6YV+HrxQ7S
Ky83q60Abdy8ft0RpSJeUkBjJVwiHu4y4j5iKC1tNgtV8qE9Zf2g5vAHzL3obqnu
IMr8JpmWp0MrrUa9jYOtKXk2LnZnfxurJ74NVk2RmuN5I/H0a/tUrHWtCE5pcVNk
b3vmoqeFsbTs2KDCMq/gzUhHU31l4Zrlz+9DfBUxlb5fNYB5lF4FnR+5/hKgo75+
OaNjiSfp9gTH6YfFCpS0OlHmKhsRJlR2aIKpTUEG9hjSg3Oh7XlpJHhWolQQ2BeL
++3UOyRMTDSTZ1bGa92oz5nS+UUsE5noUZSjLM+KbaJjZGCxzO9y2wiFBbRSbhL2
zXpUD2dMB1G30jZwytjn15VAMEOYizBoHEp2Nf9PNhsDGa32AcpJ2a0n89pbSOlu
yr/vEzYjJ2DZ/TWQQb7upi0G2kRX17UIZ5ZfhjmBAgMBAAGjgcswgcgwHQYDVR0O
BBYEFGu/H4b/gn8RzL7XKHBT6K4BQcl7MIGIBgNVHSMEgYAwfoAUa78fhv+CfxHM
vtcocFPorgFByXuhW6RZMFcxCzAJBgNVBAYTAlVTMRswGQYDVQQKExJXV1Bhc3Mg
Q29ycG9yYXRpb24xKzApBgNVBAMTIldXUGFzcyBDb3Jwb3JhdGlvbiBQcmltYXJ5
IFJvb3QgQ0GCCQDeyWVJYJRp+DAPBgNVHRMBAf8EBTADAQH/MAsGA1UdDwQEAwIB
BjANBgkqhkiG9w0BAQsFAAOCAgEAE46CMikI7378mkC3qZyKcVxkNfLRe3eD4h04
OO27rmfZj/cMrDDCt0Bn2t9LBUGBdXfZEn13gqn598F6lmLoObtN4QYqlyXrFcPz
FiwQarba+xq8togxjMkZ2y70MlV3/PbkKkwv4bBjOcLZQ1DsYehPdsr57C6Id4Ee
kEQs/aMtKcMzZaSipkTuXFxfxW4uBifkH++tUASD44OD2r7m1UlSQ5viiv3l0qvA
B89dPifVnIeAvPcd7+GY2RXTZCw36ZipnFiOWT9TkyTDpB/wjWQNFrgmmQvxQLeW
BWIUSaXJwlVzMztdtThnt/bNZNGPMRfaZ76OljYB9BKC7WUmss2f8toHiys+ERHz
0xfCTVhowlz8XtwWfb3A17jzJBm+KAlQsHPgeBEqtocxvBJcqhOiKDOpsKHHz+ng
exIO3elr1TCVutPTE+UczYTBRsL+jIdoIxm6aA9rrN3qDVwMnuHThSrsiwyqOXCz
zjCaCf4l5+KG5VNiYPytiGicv8PCBjwFkzIr+LRSyUiYzAZuiyRchpdT+yRAfL7q
qHBuIHYhG3E47a3GguwUwUGcXR+NjrSmteHRDONOUYUCH41hw6240Mo1lL4F+rpr
LEBB84k3+v+AtbXePEwvp+o1nu/+1sRkhqlNFHN67vakqC4xTxiuPxu6Pb/uDeNI
ip0+E9I=
-----END CERTIFICATE-----'''

WWPassData = Mapping[str, str]

class WWPassException(IOError):
    pass

class WWPassConnection(object):
    def __init__(self, keyFile, certFile, timeout = DEFAULT_TIMEOUT, spfeAddress = SPFE_ADDRESS, caFile = None):
        # type: (str, str, int, str, Optional[str]) -> None
        self.context = SSLContext(protocol = PROTOCOL_TLSv1_2)
        self.context.load_cert_chain(certfile = certFile, keyfile = keyFile)
        if caFile is None:
            self.context.load_verify_locations(cadata = DEFAULT_CADATA)
        else:
            self.context.load_verify_locations(cafile = caFile)
        self.spfeAddress = spfeAddress if spfeAddress.find('://') >= 0 else 'https://' + spfeAddress
        self.timeout = timeout
        self.connectionLock = None # type: Optional[Lock]

    def makeRequest(self, method, command, ttl = 0, container = '', authTypes = (), lock = False, unlock = False, finalize = False, attempts = 3, **kwargs):
        # type: (str, str, int, Union[str, bytes], Iterable[str], bool, bool, bool, int, **Union[str, bytes, int, None]) -> WWPassData
        kwargs['ttl'] = ttl or None
        kwargs['container'] = container or None
        kwargs['auth_type'] = self.validateAuthTypes(authTypes) or None
        kwargs['lock'] = 1 if lock else None
        kwargs['unlock'] = 1 if unlock else None
        kwargs['finalize'] = 1 if finalize else None
        kwargs = { k: v.encode('UTF-8') if isinstance(v, str) else v for (k, v) in kwargs.items() if v is not None }
        while True:
            try:
                if method == GET:
                    response = urlopen(self.spfeAddress + '/' + command + '?' + urlencode(kwargs), context = self.context, timeout = self.timeout) # type: Any
                else:
                    response = urlopen(self.spfeAddress + '/' + command, data = urlencode(kwargs).encode('UTF-8'), context = self.context, timeout = self.timeout)
                ret = pickleLoads(response.read())
                assert isinstance(ret, Mapping)
                if not ret['result']:
                    raise WWPassException("SPFE returned error: %s%s" % (ret['code'] + ': ' if 'code' in ret else '', ret['data']))
                return ret
            except URLError:
                if attempts <= 1:
                    raise
                attempts -= 1

    @staticmethod
    def validateAuthTypes(authTypes): # type: (Iterable[str]) -> str
        return ''.join(a for a in authTypes if a in VALID_AUTH_TYPES)

    def getName(self): # type: () -> str
        ticket = self.getTicket(ttl = 0)['ticket']
        pos = ticket.find(':')
        if pos == -1:
            raise WWPassException("Cannot extract service provider name from ticket")
        return ticket[:pos]

    def getTicket(self, ttl = 0, authTypes = ()): # type: (int, Iterable[str]) -> WWPassData
        result = self.makeRequest(GET, 'get', ttl = ttl, authTypes = authTypes)
        return {'ticket': result['data'], 'ttl': result['ttl']}

    def getPUID(self, ticket, authTypes = (), finalize = False): # type: (Union[str, bytes], Iterable[str], bool) -> WWPassData
        result = self.makeRequest(GET, 'puid', ticket = ticket, authTypes = authTypes, finalize = finalize)
        return {'puid': result['data']}

    def putTicket(self, ticket, ttl = 0, authTypes = (), finalize = False): # type: (Union[str, bytes], int, Iterable[str], bool) -> WWPassData
        result = self.makeRequest(GET, 'put', ticket = ticket, ttl = ttl, authTypes = authTypes, finalize = finalize)
        return {'ticket': result['data'], 'ttl': result['ttl']}

    def readWWPassData(self, ticket, container = '', finalize = False): # type: (Union[str, bytes], Union[str, bytes], bool) -> WWPassData
        result = self.makeRequest(GET, 'read', ticket = ticket, container = container, finalize = finalize)
        return {'data': result['data']}

    def readWWPassDataAndLock(self, ticket, lockTimeout, container = ''): # type: (Union[str, bytes], int, Union[str, bytes]) -> WWPassData
        result = self.makeRequest(GET, 'read', ticket = ticket, container = container, lock = True, to = lockTimeout)
        return {'data': result['data']}

    def writeWWPassData(self, ticket, data, container = '', finalize = False): # type: (Union[str, bytes], Union[str, bytes], Union[str, bytes], bool) -> bool
        self.makeRequest(POST, 'write', ticket = ticket, data = data, container = container, finalize = finalize)
        return True

    def writeWWPassDataAndUnlock(self, ticket, data, container = '', finalize = False): # type: (Union[str, bytes], Union[str, bytes], Union[str, bytes], bool) -> bool
        self.makeRequest(POST, 'write', ticket = ticket, data = data, container = container, unlock = True, finalize = finalize)
        return True

    def lock(self, ticket, lockTimeout, lockid): # type: (Union[str, bytes], int, Union[str, bytes]) -> bool
        self.makeRequest(GET, 'lock', ticket = ticket, lockid = lockid, to = lockTimeout)
        return True

    def unlock(self, ticket, lockid, finalize = False): # type: (Union[str, bytes], Union[str, bytes], bool) -> bool
        self.makeRequest(GET, 'unlock', ticket = ticket, lockid = lockid, finalize = finalize)
        return True

    def getSessionKey(self, ticket, finalize = False): # type: (Union[str, bytes], bool) -> WWPassData
        result = self.makeRequest(GET, 'key', ticket = ticket, finalize = finalize)
        return {'sessionKey': result['data']}

    def createPFID(self, data = ''): # type: (Union[str, bytes]) -> WWPassData
        result = self.makeRequest(POST, 'sp/create', data = data) if data \
            else self.makeRequest(GET, 'sp/create')
        return {'pfid': result['data']}

    def removePFID(self, pfid): # type: (Union[str, bytes]) -> bool
        self.makeRequest(POST, 'sp/remove', pfid = pfid)
        return True

    def readWWPassDataSP(self, pfid): # type: (Union[str, bytes]) -> WWPassData
        result = self.makeRequest(GET, 'sp/read', pfid = pfid)
        return {'data': result['data']}

    def readWWPassDataSPandLock(self, pfid, lockTimeout): # type: (Union[str, bytes], int) -> WWPassData
        result = self.makeRequest(GET, 'sp/read', pfid = pfid, to = lockTimeout, lock = True)
        return {'data': result['data']}

    def writeWWPassDataSP(self, pfid, data): # type: (Union[str, bytes], Union[str, bytes]) -> bool
        self.makeRequest(POST, 'sp/write', pfid = pfid, data = data)
        return True

    def writeWWPassDataSPandUnlock(self, pfid, data): # type: (Union[str, bytes], Union[str, bytes]) -> bool
        self.makeRequest(POST, 'sp/write', pfid = pfid, data = data, unlock = True)
        return True

    def lockSP(self, lockid, lockTimeout): # type: (Union[str, bytes], int) -> bool
        self.makeRequest(GET, 'sp/lock', lockid = lockid, to = lockTimeout)
        return True

    def unlockSP(self, lockid): # type: (Union[str, bytes]) -> bool
        self.makeRequest(GET, 'sp/unlock', lockid = lockid)
        return True

    def getClientKey(self, ticket): # type: (Union[str, bytes]) -> WWPassData
        result = self.makeRequest(GET, 'clientkey', ticket = ticket)
        ret = {'clientKey': result['data'], 'ttl': result['ttl']}
        if 'originalTicket' in result:
            ret['originalTicket'] = result['originalTicket']
        return ret

class WWPassConnectionMT(WWPassConnection):
    def __init__(self, keyFile, certFile, timeout = DEFAULT_TIMEOUT, spfeAddress = SPFE_ADDRESS, caFile = None, initialConnections = 2): # pylint: disable=super-init-not-called
        # type: (str, str, int, str, Optional[str], int) -> None
        self.keyFile = keyFile
        self.certFile = certFile
        self.timeout = timeout
        self.spfeAddress = spfeAddress
        self.caFile = caFile
        self.connectionPool = [] # type: List[WWPassConnection]
        for _ in xrange(initialConnections):
            self.addConnection()

    def addConnection(self, acquired = False): # type: (bool) -> WWPassConnection
        conn = WWPassConnection(self.keyFile, self.certFile, self.timeout, self.spfeAddress, self.caFile)
        conn.connectionLock = Lock()
        if acquired:
            assert conn.connectionLock
            conn.connectionLock.acquire()
        self.connectionPool.append(conn)
        return conn

    def getConnection(self): # type: () -> WWPassConnection
        for conn in self.connectionPool:
            assert conn.connectionLock
            if conn.connectionLock.acquire(False):
                return conn
        return self.addConnection(True)

    def makeRequest(self, method, command, attempts = 3, **kwargs): # type: ignore[no-untyped-def, override] # pylint: disable=arguments-differ
        conn = None
        try:
            conn = self.getConnection()
            return conn.makeRequest(method, command, attempts = attempts, **kwargs)
        finally:
            if conn:
                assert conn.connectionLock
                conn.connectionLock.release()
