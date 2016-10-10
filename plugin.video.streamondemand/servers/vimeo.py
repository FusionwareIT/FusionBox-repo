# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para Vimeo
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#------------------------------------------------------------

import re

from core import jsontools
from core import logger
from core import scrapertools


# Returns an array of possible video url's from the page_url
def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("streamondemand.servers.vimeo get_video_url(page_url='%s')" % page_url)

    if not page_url.endswith("/config"):
        page_url = find_videos(page_url)[0][1]

    video_urls = []
    data = scrapertools.downloadpage(page_url)
    json_object = jsontools.load_json(data)

    url_data = json_object['request']['files']['progressive']
    for data_media in url_data:
        media_url = data_media['url']
        title = data_media['mime'].replace("video/", ".") + " (" + data_media['quality'] + ") [vimeo]"
        video_urls.append([title, media_url])  

    video_urls.reverse()
    for video_url in video_urls:
        logger.info("streamondemand.servers.vimeo %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vÃ­deos del servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    # http://player.vimeo.com/video/17555432?title=0&amp;byline=0&amp;portrait=0
    # http://vimeo.com/17555432
    patronvideos  = '(?:vimeo.com/|player.vimeo.com/video/)([0-9]+)'
    logger.info("streamondemand.servers.vimeo find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(text)

    for match in matches:
        titulo = "[vimeo]"
        url = "https://player.vimeo.com/video/%s/config" % match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'vimeo' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
    return devuelve
