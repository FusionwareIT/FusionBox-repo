# -*- coding: utf-8 -*-

import os
import xbmc
import common

try:
    from sqlite3 import dbapi2 as sqlite
except:
    from pysqlite2 import dbapi2 as sqlite
    
SELECT_ALL_CHANNELS_GROUP = 'SELECT idGroup, sName FROM channelgroups WHERE (iGroupType=1) and (bIsRadio=%s)'  
SELECT_CHANNELS = 'SELECT cnl.sChannelName, mcnl.iChannelNumber, cnl.sIconPath, cnl.iClientId, cnl.iUniqueId FROM channels as cnl join map_channelgroups_channels as mcnl on (cnl.idChannel=mcnl.idChannel) WHERE mcnl.idGroup=%s ORDER BY mcnl.iChannelNumber'
SELECT_CLIENT_PVR = 'SELECT addonID FROM addon WHERE id=%s'
SELECT_CHANNEL_EPG = 'SELECT idEpg FROM channels WHERE iUniqueId=%s'
SELECT_EPG_DATA = 'SELECT sTitle, iStartTime, iEndTime FROM epgtags WHERE (idEpg=%s) and (iStartTime<=%s) and (iEndTime>%s) ORDER BY iStartTime LIMIT 1'
   
class DBChannels:

    __slots__ = ('DBconnect','dbTV','dbAddons', 'dbEpg')
    
    def __init__(self):
        try:
            self.dbTV = os.path.join(xbmc.translatePath("special://database"), common.NAME_TVDB)
            self.dbAddons = os.path.join(xbmc.translatePath("special://database"), common.NAME_ADDONSDB)
            self.dbEpg = os.path.join(xbmc.translatePath("special://database"), common.NAME_EPGDB)
            self.DBconnect = sqlite.connect(self.dbTV)
        except Exception, e:
            common.dbg_log('DBChannels::__init__', 'ERROR: (' + repr(e) + ')', common.logErorr)
            
    def get_id_group_row(self, vIsRadio):
        try:
            cur = self.DBconnect.cursor()
            sel_str = SELECT_ALL_CHANNELS_GROUP % str(vIsRadio)
            cur.execute(sel_str)
            return cur.fetchone()
        except Exception, e:
            common.dbg_log('DBChannels::get_id_group_row', 'ERROR: (' + repr(e) + ')', common.logErorr)        
            
    def get_id_epg(self, vUChannelID):
        try:
            cur = self.DBconnect.cursor()
            sel_str = SELECT_CHANNEL_EPG % str(vUChannelID)
            cur.execute(sel_str)
            ret = cur.fetchone()
            id_epg = ''
            if ret:
                id_epg = str(ret[0])
            return id_epg
        except Exception, e:
            common.dbg_log('DBChannels::get_id_epg', 'ERROR: (' + repr(e) + ')', common.logErorr)
     
    def get_epg_data(self, vUChannelID, vCurTime):
        try:
            epgid = self.get_id_epg(vUChannelID)
            connect = sqlite.connect(self.dbEpg)
            cur = connect.cursor()
            sel_str = SELECT_EPG_DATA % (epgid, vCurTime, vCurTime)
            cur.execute(sel_str)
            data = cur.fetchone()
            if connect:
                connect.close()
            return data
        except Exception, e:
            common.dbg_log('DBChannels::get_epg_data', 'ERROR: (' + repr(e) + ')', common.logErorr)
            
    def get_channels_list(self, vIsRadio):
        try: 
            idAGroup = self.get_id_group_row(vIsRadio)
            cur = self.DBconnect.cursor()
            sel_str = SELECT_CHANNELS % str(idAGroup[0])
            return cur.execute(sel_str)
        except Exception, e:
            common.dbg_log('DBChannels::get_channels_list', 'ERROR: (' + repr(e) + ')', common.logErorr)
            
    def get_pvr_client_name(self, vClientID):
        try:
            connect = sqlite.connect(self.dbAddons)
            cur = connect.cursor()
            sel_str = SELECT_CLIENT_PVR % vClientID
            cur.execute(sel_str)
            data = cur.fetchone()
            pvr_client_name = ''
            if data:
                pvr_client_name = data[0]
            if connect:
                connect.close()
            return pvr_client_name
        except Exception, e:
            common.dbg_log('DBChannels::get_pvr_client_name', 'ERROR: (' + repr(e) + ')', common.logErorr)        
    
    def __del__(self):
        try:
            if self.DBconnect:
                self.DBconnect.close()
        except Exception, e:
            common.dbg_log('DBChannels::__del__', 'ERROR: (' + repr(e) + ')', common.logErorr)
        