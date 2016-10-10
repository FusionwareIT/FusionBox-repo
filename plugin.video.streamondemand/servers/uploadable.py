# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para uploadable
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#------------------------------------------------------------

import re

from core import logger


def test_video_exists( page_url ):
    logger.info("streamondemand.servers.uploadable test_video_exists(page_url='%s')" % page_url)
    
    return True,""

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("streamondemand.servers.uploadable get_video_url(page_url='%s')" % page_url)
    video_urls = []
    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    # https://www.uploadable.ch/list/cKMCXrm7gZqv
    patronvideos  = 'uploadable.ch/((?:list/|file/)[\w]+)'
    logger.info("streamondemand.servers.uploadable find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[uploadable]"
        url = "https://www.uploadable.ch/"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'uploadable' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve
