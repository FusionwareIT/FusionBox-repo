# -*- coding: utf-8 -*-

import sys
import os
import common
import db
import xbmc
import xbmcgui

class SelectChannels(xbmcgui.WindowXMLDialog):
   
    def __init__(self, *args, **kwargs):
        try:
            xbmcgui.WindowXMLDialog.__init__(self)
            self.isRadio = kwargs.get("isradio")
            self.SkinPropery = kwargs.get("property")
            
            self.C_MAIN_HEADER=1
            self.C_MAIN_LIST1=3
            self.C_MAIN_LIST2=6
            self.C_MAIN_OK_BUTTON=5
            self.C_MAIN_CANCEL_BUTTON1=7
            self.C_MAIN_CANCEL_BUTTON2=99
            
            self.DBC = db.DBChannels()
        except Exception, e:
            common.dbg_log('SelectChannels::__init__', 'ERROR: (' + repr(e) + ')', common.logErorr)
    
    def onInit(self):
        try:
            try:
                self.ChannelList = self.getControl(self.C_MAIN_LIST2)
                self.getControl(self.C_MAIN_LIST1).setVisible(False)
            except:
                print_exc()
                self.ChannelList = self.getControl(self.C_MAIN_LIST1)
                
            self.getControl(self.C_MAIN_HEADER).setLabel(common.Lang(32000+int(self.isRadio)))
            self.getControl(self.C_MAIN_OK_BUTTON).setVisible(False)
            
            lstItem = xbmcgui.ListItem(common.Lang(32002))
            lstItem.setLabel2(common.Lang(32003))
            lstItem.setIconImage('DefaultAddonNone.png')
            lstItem.setProperty('IconPath','')
            lstItem.setProperty('ClientId','')
            lstItem.setProperty('UniqueId','')
            lstItem.setProperty('Addon.Summary',common.Lang(32003))
            self.ChannelList.addItem(lstItem)
            
            DBdata = self.DBC.get_channels_list(self.isRadio)
            if DBdata:
                for row in DBdata:
                    lstItem = xbmcgui.ListItem(row[0].encode('utf-8'))
                    lstItem.setLabel2(str(row[1]))
                    lstItem.setIconImage(row[2].encode('utf-8'))
                    lstItem.setProperty('IconPath',row[2].encode('utf-8'))
                    lstItem.setProperty('ClientId',str(row[3]))
                    lstItem.setProperty('UniqueId',str(row[4]))
                    lstItem.setProperty('Addon.Summary',str(row[1]))
                    self.ChannelList.addItem(lstItem)
                    
            self.setFocus(self.ChannelList)
            
        except Exception, e:
            common.dbg_log('SelectChannels::onInit', 'ERROR: (' + repr(e) + ')', common.logErorr) 

    def onAction(self, action):
        try:
            if action.getId() in (9, 10, 92, 216, 247, 257, 275, 61467, 61448,):
                self.close()
        except Exception, e:
            common.dbg_log('SelectChannels::onAction', 'ERROR: (' + repr(e) + ')', common.logErorr)                 

    def onClick(self, controlID):
        try:
            if controlID == self.C_MAIN_LIST1 or controlID == self.C_MAIN_LIST2:
                selectedPos = self.ChannelList.getSelectedPosition()
                if selectedPos > 0:
                    selectedItem = self.getControl(controlID).getSelectedItem()
                    strChannelName = selectedItem.getLabel()
                    strIconPath = selectedItem.getProperty('IconPath')                    
                    strClientId = selectedItem.getProperty('ClientId')
                    strUniqueId = selectedItem.getProperty('UniqueId')

                    ClientName = self.DBC.get_pvr_client_name(strClientId)
                    grow = self.DBC.get_id_group_row(self.isRadio)
                    sub = ['tv','radio']
                    strPatch = 'pvr://channels/%s/%s/%s_%s.pvr' % (sub[int(self.isRadio)],str(grow[1]),ClientName,strUniqueId)
                    
                    xbmc.executebuiltin('Skin.SetString(%s,%s)' % ('%s.%s' % (self.SkinPropery, "Path",), strPatch.encode('utf-8'),))
                    xbmc.executebuiltin('Skin.SetString(%s,%s)' % ('%s.%s' % (self.SkinPropery, "Number",), strUniqueId,))
                    xbmc.executebuiltin('Skin.SetString(%s,%s)' % ('%s.%s' % (self.SkinPropery, "Label",), strChannelName,))
                    xbmc.executebuiltin('Skin.SetString(%s,%s)' % ('%s.%s' % (self.SkinPropery, "Icon",), strIconPath,))
                    xbmc.sleep(300)
                    self.close()
                else:
                    xbmc.executebuiltin('Skin.Reset(%s)' % '%s.%s' % (self.SkinPropery, "Path",))
                    xbmc.executebuiltin('Skin.Reset(%s)' % '%s.%s' % (self.SkinPropery, "Number",))
                    xbmc.executebuiltin('Skin.Reset(%s)' % '%s.%s' % (self.SkinPropery, "Label",))
                    xbmc.executebuiltin('Skin.Reset(%s)' % '%s.%s' % (self.SkinPropery, "Icon",))
                    xbmc.sleep(300)
                    self.close()
                    
            if controlID == self.C_MAIN_CANCEL_BUTTON1 or controlID == self.C_MAIN_CANCEL_BUTTON2:
                self.close()
                
        except Exception, e:
            common.dbg_log('SelectChannels::onClick', 'ERROR: (' + repr(e) + ')', common.logErorr)  

    def onFocus(self, controlID):
        pass
    