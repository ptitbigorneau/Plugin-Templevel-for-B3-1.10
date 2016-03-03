# -*- coding: utf-8 -*-
#
# TempLevel plugin for BigBrotherBot(B3) (www.bigbrotherbot.net)
# Copyright (C) 2015 PtitBigorneau - www.ptitbigorneau.fr
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

__author__  = 'ptitbigorneau'
__version__ = '1.4'

import b3
import b3.plugin
from b3 import clients
import b3.cron
from b3.functions import getCmd

import datetime, time, calendar, threading, thread, re
from time import gmtime, strftime

def cdate():
        
    time_epoch = time.time() 
    time_struct = time.gmtime(time_epoch)
    date = time.strftime('%Y-%m-%d %H:%M:%S', time_struct)
    mysql_time_struct = time.strptime(date, '%Y-%m-%d %H:%M:%S')
    cdate = calendar.timegm( mysql_time_struct)
        
    return cdate

class TemplevelPlugin(b3.plugin.Plugin):

    _adminPlugin = None
    _deltest = None
    _cronTab = None
	
    def onStartup(self):

        self._adminPlugin = self.console.getPlugin('admin')
        
        if not self._adminPlugin:

            self.error('Could not find admin plugin')
            return False
        
        if 'commands' in self.config.sections():
            for cmd in self.config.options('commands'):
                level = self.config.get('commands', cmd)
                sp = cmd.split('-')
                alias = None
                if len(sp) == 2:
                    cmd, alias = sp

                func = getCmd(self, cmd)
                if func:
                    self._adminPlugin.registerCommand(self, cmd, level, func, alias)
 
        if self._cronTab:
        
            self.console.cron - self._cronTab

        self._cronTab = b3.cron.PluginCronTab(self, self.control, minute='*/1')
        self.console.cron + self._cronTab
    
    def cmd_templevel(self, data, client, cmd=None):
        """\
        - change level temporarily to a player
        """

        if data:
            
            input = self._adminPlugin.parseUserCmd(data)

        else:
            
            cmd.sayLoudOrPM(client, '!tlevel <client> <group,duration> or <client> <-u>')
            return False

        sclient = self._adminPlugin.findClientPrompt(input[0], client)

        if not sclient:

            return False

        if not input[1]:

            self.tlevels(sclient)
            
            if self.rtlevel != None:
 
                self.tgroups(self.rtlevel, client)
                cmd.sayLoudOrPM(client, '%s is temporarily ^2%s^7(^5%s^7) until : %s'%(sclient.exactName, self.rgname, self.rglevel, self.rmdatefin))
                return
            
            else:

                cmd.sayLoudOrPM(client, '%s has not a temporary level'%(sclient.exactName)) 
                return

        if input[1] == '-u':
            
            self._deltest = 'ok'
            self.tlevels(sclient)
            
            if self.rtlevel != None:
                
                test = None
                self.tgroups(self.roldlevel, client)
                                
                try:

                    group = clients.Group(keyword=self.rgkeyword)
                    group = self.console.storage.getGroup(group)
        
                except:
                    
                    test = "error"
                    client.message('Error !')            
                    return False
            
                if test == None:

                    cmd.sayLoudOrPM(client, '%s is back in group ^2%s^7(^5%s^7)'%(sclient.exactName, self.rgname, self.rglevel))   
                    cmd.sayLoudOrPM(sclient, 'you are back in group ^2%s^7(^5%s^7)'%(self.rgname, self.rglevel))
                    sclient.setGroup(group)
                    sclient.save()
            
            else:
                
                self._deltest == None
                cmd.sayLoudOrPM(client, '%s has not a temporary level'%(sclient.exactName))
            
        if input[1] != '-u':
        
            nespace= input[1].count(',')
            
            if nespace != 1:
        
                cmd.sayLoudOrPM(client, '!tlevel <client> <group,duration>')
                return False  

            data2 = input[1].split(',')

            if 'd' in data2[1]:

                duree = data2[1].replace('d','')
                aduree = 'day(s)'
                sduree = int(duree) * 86400

            elif 'h' in data2[1]:

                duree = data2[1].replace('h','')
                aduree = 'hour(s)'
                sduree = int(duree) * 3600

            elif 'm' in data2[1]:

                duree = data2[1].replace('m','')
                aduree = 'minute(s)'
                sduree = int(duree) * 60

            else:
			
                cmd.sayLoudOrPM(client, '!tlevel <client> <group,duration>')
                cmd.sayLoudOrPM(client, 'duration format xxd or xxh for xx days or xx hours')

                return False     

            self.tgroups(data2[0], client)
            self.tlevels(sclient)

            if self.rgkeyword == None:

                self.tgroups('None', client)
                return False

            if self.rtlevel != None:
 
                self.tgroups(self.rtlevel, client)
                
                cmd.sayLoudOrPM(client, '%s is already temporarily ^2%s^7(^5%s^7) until %s'%(sclient.exactName, self.rgname, self.rglevel, self.rmdatefin))          
 
                return False

            datefin = cdate() + sduree

            oldlevel = sclient.maxLevel

            cursor = self.console.storage.query("""
            INSERT INTO tlevel
            VALUES ('%s', '%s', '%s', '%s')
            """ % (sclient.id, self.rglevel, oldlevel, datefin))
            cursor.close()
              
            test = None			  
       
            try:
	
                group = clients.Group(keyword=self.rgkeyword)
                group = self.console.storage.getGroup(group)
        
            except:
                test = "error"
                cmd.sayLoudOrPM(client, 'Error !')
                return False
				
            if test == None:

                cmd.sayLoudOrPM(client, '%s is now temporarily ^2%s^7(^5%s^7) for %s %s'%(sclient.exactName, self.rgname, self.rglevel, duree, aduree))    
                cmd.sayLoudOrPM(sclient, 'you are now temporarily ^2%s^7(^5%s^7) for %s %s'%(self.rgname, self.rglevel, duree, aduree))                
                sclient.setGroup(group)
                sclient.save()

    def cmd_mytemplevel(self, data, client, cmd=None):
        """\
        - my level temporarily
        """
            
        self.tlevels(client)
            
        if self.rtlevel != None:
 
            self.tgroups(self.rtlevel, client)
            cmd.sayLoudOrPM(client, '^3You are temporarily ^2%s^7(^5%s^7) ^3until : ^5%s'%(self.rgname, self.rglevel, self.rmdatefin))
            return
            
        else:
            cmd.sayLoudOrPM(client, '^3You do not have a temporary level')
            return

    def tgroups(self, cdata, client):

        self.rgname = None
        self.rgkeyword = None
        self.rglevel = None     
    
        cursor = self.console.storage.query("""
        SELECT *
        FROM groups n 
        """)

        if cursor.EOF:
  
            cursor.close()            
            
            return False

        while not cursor.EOF:
        
            sr = cursor.getRow()
            gname= sr['name']
            gkeyword = sr['keyword']
            glevel= sr['level']
       
            if cdata == 'None':

                client.message('%s, %s, %s'%(gname, gkeyword, glevel))

            if cdata in (gname.lower(), gkeyword, glevel):

                self.rgname = gname
                self.rgkeyword = gkeyword
                self.rglevel = glevel

            cursor.moveNext()
    
        cursor.close()

    def tlevels(self, sclient):

        self.rtlevel = None     
        self.roldlevel = None
        self.mduree = None
        self.rdatefin = None 

        cursor = self.console.storage.query("""
        SELECT *
        FROM tlevel n 
        """)

        if cursor.EOF:
  
            cursor.close()            
            
            return False

        while not cursor.EOF:
        
            sr = cursor.getRow()
            gclientid= sr['client_id']
            gtlevel = sr['tlevel']
            goldlevel= sr['oldlevel']
            gdatefin = sr['datefin']  

            if sclient.id == gclientid:

                self.rtlevel = gtlevel     
                self.roldlevel = goldlevel
                self.rdatefin = gdatefin
                time_struct = time.localtime(gdatefin)
                self.rmdatefin = time.strftime('%Y-%m-%d %H:%M', time_struct)

                if self._deltest == 'ok':

                    cursor = self.console.storage.query("""
                    DELETE FROM tlevel
                    WHERE client_id = '%s'
                    """ % (sclient.id))
                    cursor.close()

                    self._deltest = None                    

            cursor.moveNext()
    
        cursor.close()

    def control(self):

        cursor = self.console.storage.query("""
        SELECT *
        FROM tlevel n 
        """)
        
        if cursor.EOF:
  
            cursor.close()            
            
            return False

        while not cursor.EOF:
            
            sr = cursor.getRow()
            clientid = sr['client_id']
            cclientid = (sr['client_id'])
            coldlevel = sr['oldlevel']
            datefin = sr['datefin']
            client = None
            sclient = None

            for x in self.console.clients.getList():

                if int(cclientid) == int(x.id):

                    sclient = x
            
            if sclient == None:

                cclientid = '@%s'%(sr['client_id'])
                sclient = self._adminPlugin.findClientPrompt(cclientid, client)

            self.cdate = cdate()

            if datefin < self.cdate:
                 
                self.tgroups(coldlevel, sclient)
                test = None
		
                try:

                    group = clients.Group(keyword=self.rgkeyword)
                    group = self.console.storage.getGroup(group)
                
                except:
                    
                    test = "error"
                    self.console.write('Error change level!') 
                    return False
                
                if test == None:				
                    
                    sclient.setGroup(group)
                    sclient.save()

                cursor = self.console.storage.query("""
                DELETE FROM tlevel
                WHERE client_id = '%s'
                """ % (clientid))
                cursor.close()
 
            cursor.moveNext()
        cursor.close()
