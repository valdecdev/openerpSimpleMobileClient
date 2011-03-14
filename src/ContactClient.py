# -*- coding: utf-8 -*-
##############################################################################
#
#    ValueDecision Simple OpenERP Mobile Client
#    Copyright (C) 2011 ValueDecision (<http://valuedecision.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import cherrypy
import xmlrpclib
import logging
from operator import itemgetter

openerp_ip = '127.0.0.1'
server_ip = '0.0.0.0'
server_port = 8081
session_timeout = 5 # 5 minutes
db = 'your_database_name_here'

server = 'http://%s:8069/xmlrpc/' % openerp_ip

pagelimit=20

class ContactClient(object):

    common = xmlrpclib.ServerProxy(server+'common')
    object = xmlrpclib.ServerProxy(server+'object')
    
    @cherrypy.expose
    def index(self):
        return self.contactlist()
        
    @cherrypy.expose
    def loginform(self):
        return getDocWrapper() % self.wrapPage('loginform',"""
            <div data-role="header">
                <h1>OpenERP Contacts</h1>
            </div>
            <div data-role="content" data-inset="true">    
              <form action="/do_login" method="POST" data-ajax="false">
                  <div data-role="fieldcontain">
                    <label for="user">User:</label>
                    <input type="text" name="username" value=""/>
                  </div>
                  <div data-role="fieldcontain">  
                    <label for="pwd">Password:</label>
                    <input type="password" name="password" value="" />
                  </div>
                  <input id="submit1" type="submit" value="Login" data-role="button" data-inline="true" data-theme="e" />
              </form>
            </div>
        """)
    
    @cherrypy.expose
    def savesettings(self, fullscreen='off'):
        cherrypy.session['fullscreen']=fullscreen
        return self.index()
        
    @cherrypy.expose
    def settings(self):
        output = """
          <form action="/savesettings" method="POST" data-ajax="false">
            <div data-role="header">
                <h1>Edit Settings</h1>
            </div>
            
            <div data-role="content"> 
                <h3>Settings<h3>
                <p>
                <div data-role="fieldcontain">
                    <label for="fullscreen" class="ui-input-text">Fullscreen Mode:</label>
                    <select name="fullscreen" id="fullscreen" data-role="slider">
                        <option value="off">Off</option>
                        <option value="on">On</option>
                    </select>
                    <input id="submit2" type="submit" value="Apply" data-icon="check" data-inline="true" data-theme="b"/>
                </div>
                </p>
            </div>
          </form>"""
        return getDocWrapper() % self.wrapPage('settings',output)
    
    @cherrypy.expose
    def about(self):
        output = """
            <div data-role="header">
                <h1>About</h1>
            </div>
            <div data-role="content"> 
   
   <p>
   Mobile Web Client to access OpenERP Address Book
   </p>
   <p>
   Copyright (C) 2011 <a href="http://www.valuedecision.com" data-rel="external">ValueDecision Ltd (www.valuedecision.com)</a>
   </p>
   <p>
   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.
   </p>
   <p>
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
   </p>
   <p>
   You should have received a copy of the GNU General Public License
   along with this program.  If not, see http://www.gnu.org/licenses.            
   </p>
   </div>
        """
        return getDocWrapper() % self.wrapPage('about',output)
        
    
    @cherrypy.expose
    def contactlist(self,pid='na',search=None,partnersonly='off',numbertype="mobile"):
        pwd = cherrypy.session.get('pwd')
        uid = cherrypy.session.get('uid')
          
        if partnersonly=='off' :
            args = [('partner_id','!=','')]
            if pid!='na': args.append(('partner_id','=',int(pid)))
            if search!=None: args.append(('name','ilike',search))
        
            address_ids=self.object.execute(db,uid,pwd,'res.partner.address','search',args,0,pagelimit,'name')
            listdata=self.getContactListData(self.object.execute(db,uid,pwd,'res.partner.address','read', \
                                                                 address_ids,['name','partner_id','phone','mobile','email']),numbertype)
            
        else:
            listdata = self.getPartnerListData(self.getClientData(search))

        header = self.wrapHeader("""
            <h1>OpenERP <br/>Contacts</h1>
                <a href="#" data-role="button" data-rel="back" data-icon="back" data-theme="b">Back</a>
                <div data-role="controlgroup" data-type="horizontal" data-inline="true" class="valdec_cg">
                    <!--<a href="/settings" data-role="button" data-rel="dialog" data-icon="grid" data-theme="b" data-iconpos="notext">Settings</a> LES2DO -->
                    <a href="/contactlist" data-role="button" data-icon="home" data-theme="b" data-ajax="false" data-transition="slide">Home</a>
                    <a href="/about" data-role="button" data-rel="dialog" data-icon="info" data-theme="b">About</a>
                </div>
        """)
        output = """
                <div data-role="content">    
                    <form action="contactlist" method="POST" data-ajax="false">
                        %s
                        <input type="hidden" name="pid" id="pid" value="%s"/>
                        <p><ul data-role="listview" data-theme="g">%s</ul></p>        
                    </form>
                </div>
        """
        return getDocWrapper() % self.wrapPage('contactlist', ''.join([header, output %(self.getSearchBox(),pid,listdata)]))
    
    @staticmethod
    def wrapPage(id,content):
        return '<div data-role="page" id="%s" data-fullscreen="%s">%s<div data-role="footer" %s><h4>ValueDecision</h4></div></div>' \
                    %(id,ContactClient.getFullScreen(),content, ContactClient.getFixed())
    
    @staticmethod
    def wrapHeader(content):
        return '<div data-role="header" %s>%s</div>' %(ContactClient.getFixed(),content)
    
    @staticmethod
    def getFixed():
        return "" if ContactClient.getFullScreen()=='false' else 'data-position="fixed"'
    
    def getClientData(self,search=None):
        pwd = cherrypy.session.get('pwd')
        uid = cherrypy.session.get('uid')
        client_ids= self.object.execute(db,uid,pwd,'res.partner','search',[('name','ilike',search or '')],0,pagelimit,'name')
        return self.object.execute(db,uid,pwd,'res.partner','read',client_ids,['id','name'])
        
    def getPartnerListData(self,data):
        output=''
        for detail in data:
            output+='<li><a href="contactlist?pid=%s" data-ajax="false" data-transition="slide">%s</a></li>' %(detail['id'],detail['name'])
        return output
        
    def getContactListData(self, data,numbertype):
        sData = sorted(data, key=itemgetter('name'))
        output=''
        for detail in sData:
            name = '%s <br/>(%s)' % (detail['name'],detail['partner_id'][1]) if detail['partner_id'] else detail['name']
            phone = detail[numbertype] if detail[numbertype] else 'No Number Held (%s)' % numbertype 
            output+='<li><a href="tel:%s"><h3>%s</h3><p class="valdec_num">%s</p></a></p><p><a href="mailto:%s" data-icon="plus" data-theme="e">email</a></p></li>' \
            %(phone,name,phone,detail['email'])
        
        return output
    
    def getSearchBox(self):
        output = """
            <div data-role="collapsible" data-collapsed="true">
                <h3>Search<h3>
                <p>
                <div data-role="fieldcontain">
                    <label for="search">Search:</label>
                    <input type="search" name="search" id="search" value="" />
                </div>
                <div data-role="fieldcontain">
                    <label for="partnersonly" class="ui-input-text">Search in:</label>
                    <select name="partnersonly" id="partnersonly" data-role="slider">
                        <option value="off">Contact</option>
                        <option value="on">Partner</option>
                    </select>
                </div>
                <div data-role="fieldcontain">
                    <label for="numbertype" class="ui-input-text">Display:</label>
                    <select name="numbertype" id="numbertype" data-role="slider">
                        <option value="mobile">Mobile</option>
                        <option value="phone">Phone</option>
                    </select>
                <input id="submit2" type="submit" value="Submit" data-inline="true" data-theme="b" />
                </div>
                </p>
            </div>
        """
        return output
    
    @staticmethod
    def getFullScreen():
        return 'true' if cherrypy.session.get('fullscreen')=='on' else 'false'

def getDocWrapper():
    return """
    <!DOCTYPE html> 
        <html> 
        <head> 
            <title>OpenERP Contacts</title> 
            <link rel="stylesheet" href="http://code.jquery.com/mobile/1.0a3/jquery.mobile-1.0a3.min.css" />
            <script type="text/javascript" src="http://code.jquery.com/jquery-1.5.1.min.js"></script>
            <script type="text/javascript" src="http://code.jquery.com/mobile/1.0a3/jquery.mobile-1.0a3.min.js"></script>
            <style type="text/css">
                .smalltext .ui-radio label { font-size: 14px; }
                .valdec_num { font-size: 14px; }
                .valdec_cg { float: right; margin: 0 }
            </style>
        </head> 
        <body> 
        %s
        </body>
        </html>""" 
    
def mainScreen(msg=None):  
    if msg is None : msg ='Not Logged In'
    
    homepage=ContactClient.wrapPage('home',
    """<div data-role="header">
         <h1>OpenERP Contacts</h1>
           <a href="loginform" data-rel="dialog" data-theme="b">Login</a>
       </div>
       <div data-role="content">%s</div>""" % msg)
    loginpage=ContactClient.wrapPage('loginform', 
    """<div data-role="header">
         <h1>OpenERP Contacts</h1>
       </div>
       <div data-role="content" data-inset="true">    
         <form action="/do_login" method="POST" data-ajax="false">
            <div data-role="fieldcontain">
              <label for="user">User:</label>
                <input type="text" name="username" value=""/>
            </div>
            <div data-role="fieldcontain">  
              <label for="pwd">Password:</label>
              <input type="password" name="password" value="" />
            </div>
            <input id="submit1" type="submit" value="Login" data-role="button" data-inline="true" data-theme="b"/>
          </form>
        </div>""")   
    return getDocWrapper() % ''.join([homepage,loginpage])

def checkLoginAndPassword(login, password):
    uid = ContactClient().common.login(db,login,password)
    if uid:
        cherrypy.session['uid']=uid
        cherrypy.session['pwd']=password
        cherrypy.log('login:%s - succeeded' % login,context='',severity=logging.INFO,traceback=False)
    else:
        cherrypy.log('login:%s - failed' % login,context='',severity=logging.INFO,traceback=False)
        return u'Sorry wrong username or password'

def loginScreen(fromPage='..',username='',error_msg=''): 
    sc = 'Not Logged In' if error_msg=='' else error_msg
    return mainScreen(sc)

cherrypy.config.update({'server.socket_host':server_ip,
                        'server.socket_port':server_port,
                        'tools.sessions.on': True,
                        'tools.sessions.timeout':session_timeout,
                        'tools.expires.secs':0,
                        'log.access_file': 'access.log',
                        'log.error_file': 'error.log'})

cherrypy.tree.mount(ContactClient(),'/',
        {'/': { 
           'tools.session_auth.on': True,
           'tools.session_auth.debug': True,
           'tools.session_auth.login_screen': loginScreen,
           'tools.session_auth.check_username_and_password': checkLoginAndPassword
        }})

cherrypy.engine.start()
cherrypy.engine.block()
