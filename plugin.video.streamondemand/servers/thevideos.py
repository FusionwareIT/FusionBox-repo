# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para thevideos
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#------------------------------------------------------------

import re

from core import jsunpack
from core import logger
from core import scrapertools

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("streamondemand.servers.thevideos url="+page_url)

    headers = [['User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14']]
    data = scrapertools.cache_page( page_url , headers=headers )

    match = scrapertools.find_single_match(data,"<script type='text/javascript'>(.*?)</script>")
    if match.startswith("eval"):
        match = jsunpack.unpack(match)

    # Extrae la URL
    #{file:"http://95.211.81.229/kj2vy4rle46vtaw52bsj4ooof6meikcbmwimkrthrahbmy4re3eqg3buhoza/v.mp4",label:"240p"
    video_urls = []
    media_urls = scrapertools.find_multiple_matches(match,'\{file\:"([^"]+)",label:"([^"]+)"')
    for media_url, quality in media_urls:
        video_urls.append( [ media_url[-4:]+" [thevideos] "+quality, media_url])

    for video_url in video_urls:
        logger.info("streamondemand.servers.thevideos %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):

    # Añade manualmente algunos erróneos para evitarlos
    encontrados = set()
    devuelve = []

    #http://thevideos.tv/fxp1ffutzw2y.html
    #http://thevideos.tv/embed-fxp1ffutzw2y.html
    patronvideos  = 'thevideos.tv/(?:embed-|)([a-z0-9A-Z]+)'
    logger.info("streamondemand.servers.thevideos find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[thevideos]"
        url = "http://thevideos.tv/embed-%s.html" % match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'thevideos' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve
