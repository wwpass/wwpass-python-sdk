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
ERROR = open('templates/error.html').read()

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
        
        if 'wwpass_status' in postvars and 'wwpass_response' in postvars:
            if postvars['wwpass_status'][0] == '200':
                ticket = postvars['wwpass_response'][0]
                status, response = conn.getPUID(ticket)
                if status:
                    # Success
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(PUID.replace('{{ PUID }}', response))
                else:
                    # Error — getPuid
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(ERROR.replace('{{ ERROR }}', response))
            else:
                # Error — authentication 
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(ERROR.replace('{{ ERROR }}', '%s: %s' % (
                    postvars['wwpass_status'][0],
                    postvars['wwpass_response'][0]
                    )))
        else:
            # Error — not found wwpass_status
            self.send_error(400, 'Bad request: lost params wwpass_status or wwpass_response.')

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
