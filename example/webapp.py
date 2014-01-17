# -*- coding: utf-8 -*-

import cgi
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

from wwpass import WWPASSConnectionMT

PORT = 80
SPNAME = None

FCA = 'wwpass.ca.crt'
FKEY = 'sdk.test.key'
FCERT = 'sdk.test.crt'

conn = WWPASSConnectionMT(FKEY, FCERT, 15, 'https://spfe.wwpass.com', FCA, 0)

if not SPNAME:
    status, SPNAME = conn.getName()
    if not status:
        exit('Connection fail :(')

# load templates
HOME = open('templates/home.html').read()
PUID = open('templates/puid.html').read()

class HelloHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != '/':
            self.send_error(404, 'File Not Found: %s' % self.path)
            return
        
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(HOME.replace('{{ SPNAME }}', SPNAME))
    
    def do_POST(self):
        if self.path != '/':
            self.send_error(404, 'File Not Found: %s' % self.path)
            return
        
        
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = {}
        
        print repr(postvars)
        
        if 'wwpass_status' in postvars and postvars['wwpass_status'][0] == '200':
            # Success
            ticket = postvars['wwpass_response'][0]
            print 'ticket -- %s' % ticket
            status, response = conn.getPUID(ticket)
            if status:
                
                print 'puid -- %s' % response
                
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(PUID.replace('{{ PUID }}', response))
                
            else:
                # Error — authentication 
                pass
        else:
            # Error — no wwpass status
            pass
            
            
        


def main():
    try:
        server = HTTPServer(('10.25.11.131', 1180), HelloHandler)
        print 'Started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()
