# -*- coding: utf-8 -*-
__author__ = "Rostislav Kondratenko <r.kondratenko@wwpass.com>"
__date__ = "$27.11.2014 18:05:15$"

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

# These are Python 3 recommendations that are not valid for Python 2 compatible code:
# pylint: disable=consider-using-assignment-expr, consider-using-f-string, useless-object-inheritance

from pickle import loads as pickleLoads
from ssl import SSLContext, PROTOCOL_TLSv1_2
from threading import Lock

try:
    from typing import Any, Iterable, List, Mapping, Optional, Union  # pylint: disable=unused-import, useless-suppression  # noqa: E501
    WWPassData = Mapping[str, Union[bytes, int]]
    String = Union[str, bytes]
except ImportError:  # typing is absent in Python 2 unless installed explicitly via pip
    WWPassData = dict  # type: ignore[misc]
    String = str  # type: ignore[misc] # pylint: disable=redefined-variable-type, useless-suppression # pylint 2/3 warnings  # noqa: E501

import sys
if sys.version_info[0] == 2:
    # Python 2
    from urllib2 import urlopen
    from urllib import urlencode, addinfourl  # pylint: disable=unused-import, useless-suppression # pylint 3/2 warnings
else:  # Python 3
    from urllib.request import urlopen      # pylint: disable=import-error, no-name-in-module, useless-suppression # pylint 2/3 warnings  # noqa: E501
    from urllib.response import addinfourl  # pylint: disable=import-error, no-name-in-module, useless-suppression # pylint 2/3 warnings  # noqa: E501
    from urllib.parse import urlencode      # pylint: disable=import-error, no-name-in-module, useless-suppression # pylint 2/3 warnings  # noqa: E501
    xrange = range                          # pylint: disable=redefined-builtin,               useless-suppression # pylint 2/3 warnings  # noqa: E501

# HTTP methods
GET = 'GET'
POST = 'POST'

SPFE_ADDRESS = 'spfe.wwpass.com'
DEFAULT_TIMEOUT = 10

# Auth factors
PIN = 'p'
SESSION_KEY = 's'
CLIENT_KEY = 'c'
MESSAGE = 'm'

VALID_AUTH_TYPES = PIN + SESSION_KEY + CLIENT_KEY + MESSAGE

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


class WWPassException(IOError):
    pass


class WWPassConnection(object):
    def __init__(self,
                 key_file,                   # type: str
                 cert_file,                  # type: str
                 timeout=DEFAULT_TIMEOUT,    # type: int
                 spfe_address=SPFE_ADDRESS,  # type: str
                 ca_file=''                  # type: str
                 ):                          # type: (...) -> None
        self.context = SSLContext(protocol=PROTOCOL_TLSv1_2)
        self.context.check_hostname = True
        self.context.load_cert_chain(certfile=cert_file, keyfile=key_file)
        if ca_file:
            self.context.load_verify_locations(cafile=ca_file)
        else:
            self.context.load_verify_locations(cadata=DEFAULT_CADATA)
        self.spfe_address = spfe_address[8:] if spfe_address.lower().startswith('https://') else spfe_address
        self.timeout = timeout
        self.connection_lock = None  # type: Optional[Lock] # For WWPassConnectionMT

    def close(self):  # type: () -> None
        pass

    def __enter__(self):  # type: () -> WWPassConnection
        return self

    def __exit__(self, *_args, **_kwargs):  # type: (*Any, **Any) -> None
        self.close()

    def makeRequest(self,
                    method,         # type: str
                    command,        # type: str
                    auth_types=(),  # type: Iterable[str]
                    **kwargs        # type: Any
                    ):              # type: (...) -> WWPassData
        assert method in (GET, POST)
        kwargs['auth_type'] = ''.join(a for a in auth_types if a in VALID_AUTH_TYPES)
        cgi_string = urlencode({k: (1 if v is True else v) for (k, v) in kwargs.items() if v})
        url = 'https://' + self.spfe_address + '/' + command + \
              ('?' + cgi_string if method == GET and cgi_string else '')
        data = cgi_string.encode('UTF-8') if method == POST else None
        conn = urlopen(url, data, context=self.context, timeout=self.timeout)  # type: addinfourl
        ret = pickleLoads(conn.read())
        conn.close()
        assert isinstance(ret, dict)
        if not ret['result']:
            raise WWPassException("SPFE returned error: %s%s" %
                                  (ret['code'] + ': ' if 'code' in ret else '', ret['data']))
        return ret

    def getName(self):
        # type: () -> bytes
        ticket = self.getTicket()['ticket']
        assert isinstance(ticket, bytes)
        pos = ticket.find(b':')
        if pos == -1:
            raise WWPassException("Cannot extract service provider name from ticket")
        return ticket[:pos]

    def getTicket(self, ttl=0, auth_types=()):
        # type: (int, Iterable[str]) -> WWPassData
        result = self.makeRequest(GET, 'get', ttl=ttl, auth_types=auth_types)
        return {'ticket': result['data'], 'ttl': result['ttl']}

    def getPUID(self, ticket, auth_types=(), finalize=False):
        # type: (String, Iterable[str], bool) -> WWPassData
        result = self.makeRequest(GET, 'puid', ticket=ticket, auth_types=auth_types, finalize=finalize)
        return {'puid': result['data']}

    def putTicket(self, ticket, ttl=0, auth_types=(), finalize=False):
        # type: (String, int, Iterable[str], bool) -> WWPassData
        result = self.makeRequest(GET, 'put', ticket=ticket, ttl=ttl, auth_types=auth_types, finalize=finalize)
        return {'ticket': result['data'], 'ttl': result['ttl']}

    def readData(self, ticket, container=b'', finalize=False):
        # type: (String, String, bool) -> WWPassData
        result = self.makeRequest(GET, 'read', ticket=ticket, container=container, finalize=finalize)
        return {'data': result['data']}

    def readDataAndLock(self, ticket, lock_timeout, container=b''):
        # type: (String, int, String) -> WWPassData
        result = self.makeRequest(GET, 'read', ticket=ticket, container=container, lock=True, to=lock_timeout)
        return {'data': result['data']}

    def writeData(self, ticket, data, container=b'', finalize=False):
        # type: (String, String, String, bool) -> bool
        self.makeRequest(POST, 'write', ticket=ticket, data=data, container=container, finalize=finalize)
        return True

    def writeDataAndUnlock(self, ticket, data, container=b'', finalize=False):
        # type: (String, String, String, bool) -> bool
        self.makeRequest(POST, 'write', ticket=ticket, data=data, container=container, unlock=True, finalize=finalize)
        return True

    def lock(self, ticket, lock_timeout, lockid):
        # type: (String, int, String) -> bool
        self.makeRequest(GET, 'lock', ticket=ticket, lockid=lockid, to=lock_timeout)
        return True

    def unlock(self, ticket, lockid, finalize=False):
        # type: (String, String, bool) -> bool
        self.makeRequest(GET, 'unlock', ticket=ticket, lockid=lockid, finalize=finalize)
        return True

    def getSessionKey(self, ticket, finalize=False):
        # type: (String, bool) -> WWPassData
        result = self.makeRequest(GET, 'key', ticket=ticket, finalize=finalize)
        return {'sessionKey': result['data']}

    def createPFID(self, data=b''):
        # type: (String) -> WWPassData
        result = self.makeRequest(POST if data else GET, 'sp/create', data=data)
        return {'pfid': result['data']}

    def removePFID(self, pfid):
        # type: (String) -> bool
        self.makeRequest(POST, 'sp/remove', pfid=pfid)
        return True

    def readDataSP(self, pfid):
        # type: (String) -> WWPassData
        result = self.makeRequest(GET, 'sp/read', pfid=pfid)
        return {'data': result['data']}

    def readDataSPandLock(self, pfid, lock_timeout):
        # type: (String, int) -> WWPassData
        result = self.makeRequest(GET, 'sp/read', pfid=pfid, to=lock_timeout, lock=True)
        return {'data': result['data']}

    def writeDataSP(self, pfid, data):
        # type: (String, String) -> bool
        self.makeRequest(POST, 'sp/write', pfid=pfid, data=data)
        return True

    def writeDataSPandUnlock(self, pfid, data):
        # type: (String, String) -> bool
        self.makeRequest(POST, 'sp/write', pfid=pfid, data=data, unlock=True)
        return True

    def lockSP(self, lockid, lock_timeout):
        # type: (String, int) -> bool
        self.makeRequest(GET, 'sp/lock', lockid=lockid, to=lock_timeout)
        return True

    def unlockSP(self, lockid):
        # type: (String) -> bool
        self.makeRequest(GET, 'sp/unlock', lockid=lockid)
        return True

    def getClientKey(self, ticket):
        # type: (String) -> WWPassData
        result = self.makeRequest(GET, 'clientkey', ticket=ticket)
        ret = {'clientKey': result['data'], 'ttl': result['ttl']}
        if 'originalTicket' in result:
            ret['originalTicket'] = result['originalTicket']
        return ret


class WWPassConnectionMT(WWPassConnection):
    def __init__(self,  # pylint: disable=super-init-not-called
                 key_file,                   # type: str
                 cert_file,                  # type: str
                 timeout=DEFAULT_TIMEOUT,    # type: int
                 spfe_address=SPFE_ADDRESS,  # type: str
                 ca_file='',                 # type: str
                 initial_connections=2,      # type: int
                 ):                          # type: (...) -> None
        self.key_file = key_file
        self.cert_file = cert_file
        self.timeout = timeout
        self.spfe_address = spfe_address
        self.ca_file = ca_file
        self.connection_pool = []  # type: List[WWPassConnection]
        for _ in xrange(initial_connections):
            self.addConnection()

    def close(self):  # type: () -> None
        for conn in self.connection_pool:
            conn.close()

    def __enter__(self):  # type: () -> WWPassConnectionMT
        return self

    def addConnection(self, acquired=False):  # type: (bool) -> WWPassConnection
        conn = WWPassConnection(self.key_file, self.cert_file, self.timeout, self.spfe_address, self.ca_file)
        conn.connection_lock = Lock()
        if acquired:
            conn.connection_lock.acquire()  # pylint: disable=consider-using-with
        self.connection_pool.append(conn)
        return conn

    def getConnection(self):  # type: () -> WWPassConnection
        for conn in self.connection_pool:
            assert conn.connection_lock
            if conn.connection_lock.acquire(False):
                return conn
        return self.addConnection(True)

    def makeRequest(self,     # type: ignore[no-untyped-def, override]  # pylint: disable=arguments-differ
                    method,   # type: str
                    command,  # type: str
                    **kwargs  # type: Any
                    ):        # type: (...) -> WWPassData
        conn = None
        try:
            conn = self.getConnection()
            return conn.makeRequest(method, command, **kwargs)
        finally:
            if conn:
                assert conn.connection_lock
                conn.connection_lock.release()
