# -*- coding: utf-8 -*-

import os
import sys
import locale
import xbmc
import xbmcaddon
import xbmcgui

__author__ = 'YLLOW_DRAGON'
__scriptname__ = 'PVR favourites'
__scriptid__ = 'script.pvr.favourites'
__addon__ = xbmcaddon.Addon(__scriptid__)
__cwd__ = __addon__.getAddonInfo('path')
__common__ = sys.modules[globals()['__name__']]
__resources__ = xbmc.translatePath(os.path.join(__cwd__, 'resources'))
__resources_lib__ = xbmc.translatePath(os.path.join(__resources__, 'lib'))

debug = 'true'
logErorr = xbmc.LOGERROR

NAME_TVDB = 'TV29.db'
NAME_ADDONSDB = 'Addons20.db'  
NAME_EPGDB = 'Epg11.db'

sys.path.append(__resources_lib__)
encoding = locale.getpreferredencoding(do_setlocale=True)
reload(sys)
sys.setdefaultencoding(encoding)

def Lang(vcode):
    return __addon__.getLocalizedString(vcode)
    
def dbg_log(vsource, vtext, vlevel=xbmc.LOGNOTICE):
    if debug == 'false':
        return
    xbmc.log('## '+__scriptname__+' ## ' + vsource + ' ## ' + vtext, vlevel)