# -*- coding: utf-8 -*-

import sys
import os
import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
import time
from xml.dom.minidom import parse
import db
import gui
import common

class Main:
    def __init__(self):
        try:
            self._parse_argv()
            if self.PROPERTY == '':
                found, settings = self._read_file()
                self._set_properties(settings)
            else:
                ShowDialog(self.ISRADIO, self.PROPERTY)
        except Exception, e:
            common.dbg_log('Main::__init__', 'ERROR: (' + repr(e) + ')', common.logErorr) 
            
    def _parse_argv(self):
        try:
            try:
                params = dict(arg.split("=") for arg in sys.argv[ 1 ].split("&"))
            except:
                params = {}
            self.PROPERTY = params.get("property", "")
            self.ISRADIO = params.get("isradio", 0)
        except Exception, e:
            common.dbg_log('Main::_parse_argv', 'ERROR: (' + repr(e) + ')', common.logErorr)
            
    def _read_file(self):
        try:
            self.settings_file = xbmc.translatePath('special://profile/addon_data/'+xbmc.getSkinDir()+'/settings.xml').decode("utf-8")
            if xbmcvfs.exists(self.settings_file):
                found = True
                self.doc = parse(self.settings_file)
                settings = self.doc.documentElement.getElementsByTagName('setting')
            else:
                found = False
                settings = []
            return found, settings
        except Exception, e:
            common.dbg_log('Main::_read_file', 'ERROR: (' + repr(e) + ')', common.logErorr)
            
    def _get_strTime(self, vsecTime):
        try:
            timeStr = time.strftime('%H:%M', time.localtime(vsecTime))
            if timeStr[0] == '0':
                timeStr = timeStr[1:]
            return timeStr
        except Exception, e:
            common.dbg_log('Main::_get_strTime', 'ERROR: (' + repr(e) + ')', common.logErorr)

    def _set_properties(self, listing):
        try:
            self.WINDOW = xbmcgui.Window(10000)
            for count, setting in enumerate(listing):
                name = setting.attributes[ 'id' ].nodeValue
                aname = name.split('.')
                try:
                    value = setting.childNodes [ 0 ].nodeValue
                except:
                    value = ""
                if name.startswith('Channel') and name.endswith('.Number') and value:
                    strCurTime = str(int(time.time()))
                    
                    strTitle = ''
                    strStartTime = xbmc.getInfoLabel('System.Time(h:mm)')
                    strEndTime = xbmc.getInfoLabel('System.Time(h:mm)')
                                        
                    self.DBC = db.DBChannels()
                    epg_data = self.DBC.get_epg_data(value,strCurTime)
                    if epg_data:
                        strTitle = epg_data[0].encode('utf-8')
                        strStartTime = self._get_strTime(int(epg_data[1]))
                        strEndTime = self._get_strTime(int(epg_data[2]))
                                        
                    self.WINDOW.setProperty(aname[0]+'.'+aname[1]+'.StartTime' , strStartTime)
                    self.WINDOW.setProperty(aname[0]+'.'+aname[1]+'.EndTime' , strEndTime)
                    self.WINDOW.setProperty(aname[0]+'.'+aname[1]+'.Title' , strTitle)
        except Exception, e:
            common.dbg_log('Main::_set_properties', 'ERROR: (' + repr(e) + ')', common.logErorr)

def ShowDialog(vRadio, vProperty):
    try:
        dlg = gui.SelectChannels('DialogSelect.xml',xbmcaddon.Addon().getAddonInfo('path').decode('utf-8'), isradio=vRadio, property=vProperty)
        dlg.doModal()
        del dlg
    except Exception, e:
        common.dbg_log('ShowDialog', 'ERROR: (' + repr(e) + ')', common.logErorr)