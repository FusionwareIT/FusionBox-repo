# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para stormo
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#------------------------------------------------------------

import re

from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("streamondemand.servers.stormo test_video_exists(page_url='%s')" % page_url)
    
    data = scrapertools.downloadpage(page_url)
    if "video_error.mp4" in data: return False, "[Stormo] El archivo no existe o ha sido borrado"

    return True, ""


def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("streamondemand.servers.stormo url=" + page_url)
    
    video_urls = []
    data = scrapertools.downloadpage(page_url)
    media_url = scrapertools.find_single_match(data, 'file:"(.*?)/"')

    video_urls.append([scrapertools.get_filename_from_url(media_url)[-4:]+" [stormo]", media_url])
    for video_url in video_urls:
        logger.info("streamondemand.servers.stormo %s - %s" % (video_url[0],video_url[1]))

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    # http://www.stormo.tv/embed/84575
    patronvideos  = "stormo.tv/(?:videos/|embed/)([0-9]+)"
    logger.info("streamondemand.servers.stormo find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[stormo]"
        url = "http://stormo.tv/embed/%s" % match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'stormo' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve
