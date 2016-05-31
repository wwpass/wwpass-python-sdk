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

import locale
import sys
import os
import pickle
import pycurl as p
import StringIO
import urllib
from threading import Lock

class WWPassConnection:
    def __init__(self, key_file, cert_file, timeout=10, spfe_addr='https://spfe.wwpass.com', cafile=None):
        self.conn = p.Curl()
        if (cafile):
            self.conn.setopt(p.SSL_VERIFYPEER, True)
            self.conn.setopt(p.CAINFO, cafile)
        else:
            self.conn.setopt(p.SSL_VERIFYPEER, False)
        self.conn.setopt(p.TIMEOUT_MS,(int)(timeout*1000))
        self.conn.setopt(p.SSLCERT, cert_file)
        self.conn.setopt(p.SSLKEY, key_file)
        self.spfe_addr = "https://%s"%spfe_addr if spfe_addr.find('://') == -1 else spfe_addr

    def makeRequest(self, method, command, attempts=3,**paramsDict):
        params = {k:v.encode('UTF-8') if type(v)==unicode else v for k, v in paramsDict.iteritems() if v != None}
        try:
            if method == 'GET':
                self.conn.setopt(p.HTTPGET, 1)
                self.conn.setopt(p.URL, self.spfe_addr + '/'+command+'?'+urllib.urlencode(params))
            else:
                self.conn.setopt(p.POST, 1)
                self.conn.setopt(p.URL, self.spfe_addr + '/'+command)
                data = urllib.urlencode(params)
                self.conn.setopt(p.POSTFIELDS, data)
            b = StringIO.StringIO()
            self.conn.setopt(p.WRITEFUNCTION, b.write)
            self.conn.perform()
            res = pickle.loads(b.getvalue())
            return res['result'],res['data']
        except p.error, e:
            if attempts>0:
                attempts -= 1
                return self.makeRequest(method, command, attempts,**params)
            else:
                raise
        except Exception, e:
            return False, str(e)
        
    def getName(self):
        (status, ticket) = self.getTicket(0)
        pos = ticket.find(':')
        if pos == -1:
            return False, "SPFE returned ticket without a colon"
        return True, ticket[:pos]

    def getTicket(self, ttl=None, auth_types=""):
        return self.makeRequest('GET','get', ttl=ttl or None, auth_type=auth_types or None)

    def getPUID(self, ticket, auth_types="", finalize=None):
        return self.makeRequest('GET','puid', ticket=ticket, auth_type=auth_types or None, finalize=finalize)

    def putTicket(self, ticket, ttl=None, auth_types=""):
        return self.makeRequest('GET','put', ticket=ticket, ttl=ttl or None, auth_type=auth_types or None)

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
        for i in xrange(initial_connections):
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
        else:
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