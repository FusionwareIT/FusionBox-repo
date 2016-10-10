# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para cloudy
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def test_video_exists( page_url ):
    logger.info("streamondemand.servers.cloudy test_video_exists(page_url='%s')" % page_url)
    
    return True, ""


def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    
    logger.info("streamondemand.servers.clouddy get_video_url(page_url='%s')" % page_url)
    
    video_urls = []
    
    request_headers = []
    request_headers.append(["User-Agent","Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; es-ES; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12"])
    body,response_headers = scrapertools.read_body_and_headers(page_url,headers=request_headers)
    
    patron = 'key: "([^"]+).*?file:"([^"]+)"'
    param = re.compile(patron,re.DOTALL).findall(body)
    url_get_video ='https://www.cloudy.ec/api/player.api.php?user=&cid2=&pass=&numOfErrors=0&key=<clave>&file=<fichero>&cid3='
    url_get_video = url_get_video.replace("<clave>", param[0][0])
    url_get_video = url_get_video.replace("<fichero>", param[0][1])
    
    request_headers.append(["referer",page_url])
    request_headers.append(["accept-encoding", "gzip, deflate, sdch"])
    request_headers.append(["x-requested-with","ShockwaveFlash/20.0.0.286"])
    request_headers.append(["accept-language", "es-ES,es;q=0.8"])
        
    body,request_headers = scrapertools.read_body_and_headers(url_get_video,headers=request_headers)
    
    body = urllib.unquote(body)
     
    video = re.findall("url=(.*?)&title", body, re.DOTALL)
    
    video_urls.append([scrapertools.get_filename_from_url(video[0])[-4:],video[0] ]) 
    
    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    
    encontrados = set()
    devuelve = []

    patronvideos  = 'https://www.cloudy.ec/embed.php\?id=(.*?&width=.*?&height=\d\d\d)'
    logger.info("streamondemand.servers.cloudy find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[cloudy]"
        url = "https://www.cloudy.ec/embed.php?id="+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'cloudy' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve
