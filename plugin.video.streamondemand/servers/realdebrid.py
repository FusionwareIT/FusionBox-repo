# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para Real_Debrid
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urllib2,urllib,re

from core import scrapertools
from core import logger
from core import config

# Returns an array of possible video url's from the page_url
def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("pelisalacarta.servers.realdebrid get_video_url( page_url='%s' , user='%s' , password='%s', video_password=%s)" % (page_url , user , "**************************"[0:len(password)] , video_password) )
    page_url = correct_url(page_url)
    # Hace el login y consigue la cookie
    post = urllib.urlencode({'user' : user, 'pass' : password})
    login_url = 'https://real-debrid.com/ajax/login.php?'+post
    
    data = scrapertools.cache_page(url=login_url)
    if data is None or not re.search('expiration', data) or not re.search(user, data):
        
        # Hace el login y consigue la cookie
        post = urllib.urlencode({'user' : user, 'pass' : password})
        login_url = 'https://real-debrid.com/ajax/login.php?'+post
    
        data = scrapertools.cache_page(url=login_url)
        if re.search('OK', data):
            logger.info("Se ha logueado correctamente en Real-Debrid ")
        else:
            patron = 'message":"(.+?)"'
            matches = re.compile(patron).findall(data)
            if len(matches)>0:
                server_error = "REAL-DEBRID: "+urllib.unquote_plus(matches[-1].replace("\\u00","%"))
            else:
                server_error = "REAL-DEBRID: Ha ocurrido un error con tu login"
            return server_error
    else:
        logger.info("Ya estas logueado en Real-Debrid")

    url = 'https://real-debrid.com/ajax/unrestrict.php?link=%s&password=%s' % (urllib.quote(page_url), video_password)
    req = urllib2.Request(url)
    req.add_header('Cookie',"cookie_accept=y; https=1; lang=es; auth="+scrapertools.find_single_match(data,'auth=(.*?);'))
    response = urllib2.urlopen(req)
    data=response.read()
    response.close()

    data = data.replace('{"error":-1,"message":"Old API used, please upgrade: https:\/\/api.real-debrid.com"}',"")
    listaDict=load_json(data)
    if 'main_link' in listaDict :
        return listaDict['main_link'].encode('utf-8')
    else :
        if 'message' in listaDict :
            msg = listaDict['message'].decode('utf-8','ignore')
            server_error = "REAL-DEBRID: " + msg
            return server_error
        else :
            return "REAL-DEBRID: No generated_link and no main_link"
    

def correct_url(url):
    if "userporn.com" in url:
        url = url.replace("/e/","/video/")
    
    if "putlocker" in url:
        url = url.replace("/embed/","/file/")
    return url

def load_json(data):
    # callback to transform json string values to utf8
    def to_utf8(dct):
        
        rdct = {}
        for k, v in dct.items() :			
            if isinstance(v, (str, unicode)):
                rdct[k] = v.encode('utf8', 'ignore')
            else :
                rdct[k] = v
        
        return rdct

    try:
        import json
    except:
        try:
            import simplejson as json
        except:
            from lib import simplejson as json

    try :       
        json_data = json.loads(data, object_hook=to_utf8)
        return json_data
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
