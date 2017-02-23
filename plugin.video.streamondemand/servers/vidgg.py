# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para vidgg
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#------------------------------------------------------------

import re

from core import jsontools
from core import logger
from core import scrapertools


def test_video_exists( page_url ):
    logger.info("streamondemand.servers.vidgg test_video_exists(page_url='%s')" % page_url)
    data = jsontools.load_json(scrapertools.cache_page("http://www.vidgg.to/api-v2/alive.php?link=" + page_url))
    if data["data"] == "NOT_FOUND" or data["data"] == "FAILED":
        return False, "[Vidgg] Il file non esiste o è stato rimosso"
    elif data["data"] == "CONVERTING":
        return False, "[Vidgg] Il file è in fase di elaborazione"
    else:
        return True, ""


def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("streamondemand.servers.vidgg get_video_url(page_url='%s')" % page_url)

    video_urls = []
    data = scrapertools.cache_page(page_url)

    mediaurls = scrapertools.find_multiple_matches(data, '<source src="([^"]+)"')
    if not mediaurls:
        id_file = page_url.rsplit("/",1)[1]
        key = scrapertools.find_single_match(data, 'flashvars\.filekey\s*=\s*"([^"]+)"')
        if not key:
            varkey = scrapertools.find_single_match(data, 'flashvars\.filekey\s*=\s*([^;]+);')
            key = scrapertools.find_single_match(data, varkey+'\s*=\s*"([^"]+)"')

        # Primera url, se extrae una url erronea necesaria para sacar el enlace
        url = "http://www.vidgg.to//api/player.api.php?cid2=undefined&cid=undefined&numOfErrors=0&user=undefined&cid3=undefined&key=%s&file=%s&pass=undefined" % (key, id_file)
        data = scrapertools.cache_page(url)
        
        url_error = scrapertools.find_single_match(data, 'url=([^&]+)&')
        url = "http://www.vidgg.to//api/player.api.php?cid2=undefined&cid=undefined&numOfErrors=1&errorUrl=%s&errorCode=404&user=undefined&cid3=undefined&key=%s&file=%s&pass=undefined" % (url_error, key, id_file)
        data = scrapertools.cache_page(url)
        mediaurls = scrapertools.find_multiple_matches(data, 'url=([^&]+)&')

    for i, mediaurl in enumerate(mediaurls):
        title = scrapertools.get_filename_from_url(mediaurl)[-4:]+" Mirror %s [vidgg]" % str(i+1)
        video_urls.append( [title, mediaurl])

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
