# -*- coding: utf-8 -*-

import cgi
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

from wwpass import WWPASSConnectionMT

###### Configuration ######
# Port to listen
PORT = 8080

# Name of Service Provider (e.g. 'mysite.com'). Leave None to autodetect
SPNAME = None

# WWPass CA certificate. Download from https://developers.wwpass.com/downloads
FCA = '/path/to/wwpass.ca.crt'

# Your Service Provider private key and certificate. By these WWPass will authenticate this server.
FKEY = '/path/to/sdk.test.key'
FCERT = '/path/to/sdk.test.crt'

# Creating multi-threaded connection
conn = WWPASSConnectionMT(FKEY, FCERT, 15, 'https://spfe.wwpass.com', FCA, 0)

# Autodetecting SPNAME if it was not set
if not SPNAME:
    status, SPNAME = conn.getName()
    if not status:
        exit('Connection fail :(')

# Loading HTML templates
HOME = open('templates/home.html').read()
PUID = open('templates/puid.html').read()
ERROR = open('templates/error.html').read()

class HelloHandler(BaseHTTPRequestHandler):
    
    # Handler to display a sign-in page.
    # It will render a HOME template with an SPNAME.
    # Javascript on this page will send the WWPASS authentication result as a POST request
    def do_GET(self):
        if self.path != '/':
            self.send_error(404, 'File Not Found: %s' % self.path)
            return
        
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(HOME.replace('{{ SPNAME }}', SPNAME))
    
    # Handler for WWPass authentication result
    # It checks the result, acquires PUID from WWPass and displays it to a user.
    def do_POST(self):
        if self.path != '/':
            self.send_error(404, 'File Not Found: %s' % self.path)
            return
        # Parsing received data
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = {}
        
        if 'wwpass_status' in postvars and 'wwpass_response' in postvars:
            # We have the response
            if postvars['wwpass_status'][0] == '200':
                # WWPass authentication is successful
                ticket = postvars['wwpass_response'][0]
                # Getting the PUID
                status, response = conn.getPUID(ticket)
                if status:
                    # Success. Displaing the PUID.
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(PUID.replace('{{ PUID }}', response))
                else:
                    # Error. Displaying error message from getPUID()
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(ERROR.replace('{{ ERROR }}', response))
            else:
                # Error in WWPass authentication. Displaying error message.
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(ERROR.replace('{{ ERROR }}', '%s: %s' % (
                    postvars['wwpass_status'][0],
                    postvars['wwpass_response'][0]
                    )))
        else:
            # Error. The data is from some other form.
            self.send_error(400, 'Bad request: no parameters wwpass_status and/or wwpass_response.')

def main():
    # Start a python built-in HTTPServer.
    try:
        server = HTTPServer(('0.0.0.0', PORT), HelloHandler)
        print 'Started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down the server'
        server.socket.close()

if __name__ == '__main__':
    main()