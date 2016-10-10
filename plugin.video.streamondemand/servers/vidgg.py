# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para vidgg
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#------------------------------------------------------------

import re

from core import logger
from core import scrapertools

def test_video_exists( page_url ):
    logger.info("streamondemand.servers.vidgg test_video_exists(page_url='%s')" % page_url)
    data = scrapertools.cache_page(page_url)
    if "This file no longer exists" in data: return False, "[Vidgg] El archivo no existe o ha sido borrado"
    return True,""

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("streamondemand.servers.vidgg get_video_url(page_url='%s')" % page_url)

    file = scrapertools.find_single_match(page_url, 'http://vidgg.to/video/([a-z0-9]+)')
    data = scrapertools.cache_page("http://vidgg.to/embed/?id=%s" % file)

    key = scrapertools.find_single_match(data, 'var fkzd="([^"]+)"')
    url = "http://www.vidgg.to/api/player.api.php?file=%s&key=%s&pass=undefined&cid3=undefined&numOfErrors=0&user=undefined&cid2=undefined&cid=undefined" % (file, key)

    data = scrapertools.downloadpageGzip(url)
    mediaurl = scrapertools.find_single_match(data, 'url=(.*?)&')
    video_urls = []
    video_urls.append( [ scrapertools.get_filename_from_url(mediaurl)[-4:]+" [vidgg]", mediaurl])

    for video_url in video_urls:
        logger.info("[vidgg.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    # http://vidgg.to/video/cf8ec93a67c45
    patronvideos  = "(?:vidgg.to|vid.gg)/(?:embed/|video/)([a-z0-9]+)"
    logger.info("streamondemand.servers.vidgg find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[vidgg]"
        url = "http://vidgg.to/video/%s" % match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'vidgg' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve