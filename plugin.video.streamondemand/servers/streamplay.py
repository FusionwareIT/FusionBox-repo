# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para streamplay
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#------------------------------------------------------------

import re

from core import jsunpack
from core import logger
from core import scrapertools

def test_video_exists( page_url ):
    logger.info("streamondemand.streamplay test_video_exists(page_url='%s')" % page_url)
    data = scrapertools.cache_page(page_url)
    if ("File was deleted" or "Not Found") in data: return False, "[Streamplay] El archivo no existe o ha sido borrado"
    return True,""

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("streamondemand.streamplay get_video_url(page_url='%s')" % page_url)
    data = scrapertools.cache_page(page_url)

    matches = scrapertools.find_single_match(data, "<script type='text/javascript'>(eval\(function\(p,a,c,k,e,d.*?)</script>")
    matchjs = jsunpack.unpack(matches).replace("\\","")

    mediaurl = scrapertools.find_single_match(matchjs, ',file:"(http://[^"]+)"')
    video_urls = []
    video_urls.append( [ scrapertools.get_filename_from_url(mediaurl)[-4:]+" [streamplay]", mediaurl])

    for video_url in video_urls:
        logger.info("[streamplay.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    # http://streamplay.to/ubhrqw1drwlx
    patronvideos  = "streamplay.to/(?:embed-|)([a-z0-9]+)(?:.html|)"
    logger.info("streamondemand.streamplay find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[streamplay]"
        url = "http://streamplay.to/embed-%s.html" % match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'streamplay' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve