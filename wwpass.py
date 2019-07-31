# -*- coding: utf-8 -*-
__author__="Rostislav Kondratenko <r.kondratenko@wwpass.com>"
__date__ ="$27.11.2014 18:05:15$"

# Copyright 2009-2016 WWPASS Corporation
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

import pickle
#import StringIO
from threading import Lock
import ssl
try:
    # python3
    from urllib.request import urlopen
    from urllib.parse import urlencode
    from urllib.error import URLError
except ImportError:
    # python2
    from urllib2 import urlopen
    from urllib import urlencode

PIN = 'p'
SESSION_KEY = 's'
CLIENT_KEY = 'c'

class WWPassConnection(object):
    def __init__(self, key_file, cert_file, timeout=10, spfe_addr='https://spfe.wwpass.com', cafile=None):
        self.context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS)
        self.context.load_cert_chain(certfile=cert_file, keyfile=key_file)
        self.context.load_verify_locations(cafile=cafile)
        self.spfe_addr = "https://%s"%spfe_addr if spfe_addr.find('://') == -1 else spfe_addr
        self.timeout = timeout

    def makeRequest(self, method, command, attempts=3,**paramsDict):
        params = {k:v.encode('UTF-8') if not isinstance(v,(bytes, int)) else v for k, v in paramsDict.items() if v != None}
        try:
            if method == 'GET':
                res = urlopen(self.spfe_addr +'/'+command+'?'+urlencode(params), context=self.context, timeout=self.timeout)
            else:
                res = urlopen(self.spfe_addr +'/'+command, data=urlencode(params).encode('UTF-8'), context=self.context, timeout=self.timeout)
            res = pickle.loads(res.read())
            if not res['result']:
                if 'code'in res:
                    raise Exception('SPFE returned error: %s: %s' %(res['code'], res['data']))
                raise Exception('SPFE returned error: %s' % res['data'])
            return res

        except (URLError, IOError) as e:
            if attempts>0:
                attempts -= 1
                return self.makeRequest(method, command, attempts,**params)
            else:
                raise

    def makeAuthTypeString(self, auth_types):
        auth_type_str = ''
        if PIN in auth_types:
            auth_type_str += 'p'
        if SESSION_KEY in auth_types:
            auth_type_str += 's'
        if CLIENT_KEY in  auth_types:
            auth_type_str += 'c'
        return auth_type_str

    def getName(self):
        ticket = self.getTicket(ttl=0)['ticket']
        pos = ticket.find(':')
        if pos == -1:
            return False, "SPFE returned ticket without a colon"
        return True, ticket[:pos]

    def getTicket(self, ttl=None, auth_types=()):
        result = self.makeRequest('GET','get', ttl=ttl or None, auth_type=self.makeAuthTypeString(auth_types) or None)
        return {'ticket' : result['data'], 'ttl' : result['ttl']}

    def getPUID(self, ticket, auth_types=(), finalize=None):
        result = self.makeRequest('GET','puid', ticket=ticket, auth_type=self.makeAuthTypeString(auth_types) or None, finalize=finalize)
        return {'puid' : result['data']}

    def putTicket(self, ticket, ttl=None, auth_types=(), finalize=None):
        result = self.makeRequest('GET','put', ticket=ticket, ttl=ttl or None, auth_type=self.makeAuthTypeString(auth_types) or None, finalize=finalize)
        return {'ticket' : result['data'], 'ttl' : result['ttl']}

    def readData(self, ticket, container='', finalize=None):
        return self.makeRequest('GET','read', ticket=ticket, container=container or None, finalize=finalize)

    def readDataAndLock(self, ticket, lockTimeout, container=''):
        return self.makeRequest('GET','read', ticket=ticket, container=container or None, lock="1", to=lockTimeout)

    def writeData(self, ticket, data, container='', finalize=None):
        return self.makeRequest('POST','write', ticket=ticket, data = data, container=container or None, finalize=finalize)

    def writeDataAndUnlock(self, ticket, data, container='', finalize=None):
        return self.makeRequest('POST','write', ticket=ticket, data = data, container=container or None, unlock="1", finalize=finalize)

    def lock(self, ticket, lockTimeout, lockid):
        return self.makeRequest('GET','lock',ticket=ticket, lockid=lockid, to=lockTimeout)

    def unlock(self, ticket, lockid, finalize=None):
        return self.makeRequest('GET','unlock', ticket=ticket, lockid=lockid, finalize=finalize)

    def getSessionKey(self, ticket, finalize=None):
        return self.makeRequest('GET','key', ticket=ticket, finalize=finalize)

    def createPFID(self, data=''):
        if data:
            return self.makeRequest('POST','sp/create', data=data)
        else:
            return self.makeRequest('GET','sp/create')

    def removePFID(self, pfid):
        return self.makeRequest('POST','sp/remove', pfid=pfid)

    def readDataSP(self, pfid):
        return self.makeRequest('GET','sp/read', pfid=pfid)

    def readDataSPandLock(self, pfid, lockTimeout):
        return self.makeRequest('GET','sp/read', pfid=pfid, to=lockTimeout, lock=1)

    def writeDataSP(self, pfid, data):
        return self.makeRequest('POST','sp/write', pfid=pfid, data=data)

    def writeDataSPandUnlock(self, pfid, data):
        return self.makeRequest('POST','sp/write', pfid=pfid, data=data, unlock=1)

    def lockSP(self, lockid, lockTimeout):
        return self.makeRequest('GET','sp/lock',lockid=lockid, to=lockTimeout)

    def unlockSP(self, lockid):
        return self.makeRequest('GET','sp/unlock',lockid=lockid)

class WWPassConnectionMT(WWPassConnection):
    def __init__(self, key_file, cert_file, timeout=10, spfe_addr='spfe.wwpass.com', ca_file=None, initial_connections=2):
        self.Pool = []
        self.key_file = key_file
        self.cert_file = cert_file
        self.ca_file = ca_file
        self.timeout = timeout
        self.spfe_addr = spfe_addr
        for _ in xrange(initial_connections):
            self.addConnection()

    def addConnection(self, acquired = False):
        c = WWPassConnection(self.key_file, self.cert_file, self.timeout, self.spfe_addr, self.ca_file)
        c.lock = Lock()
        if acquired:
            c.lock.acquire()
        self.Pool.append(c)
        return c

    def getConnection(self):
        for conn in (c for c in self.Pool if c.lock.acquire(False)):
            return conn
        conn=self.addConnection(True)
        return conn

    def makeRequest(self, method, command, attempts=3,**paramsDict):
        conn = None
        try:
            conn = self.getConnection()
            return conn.makeRequest(method, command, attempts, **paramsDict)
        finally:
            if conn != None:
                conn.lock.release()

WWPASSConnection = WWPassConnection
WWPASSConnectionMT = WWPassConnectionMT
