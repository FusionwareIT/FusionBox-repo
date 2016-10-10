# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para thevideo.me
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------

import re

from core import logger
from core import scrapertools


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("streamondemand.servers.thevideome url=" + page_url)
    if not "embed" in page_url:
        page_url = page_url.replace("http://thevideo.me/","http://thevideo.me/embed-") + ".html"

    data = scrapertools.cache_page(page_url)
    tkn = scrapertools.find_single_match(data, "tkn='([^']+)'")
    data_vt = scrapertools.downloadpage("http://thevideo.me/jwv/%s" % tkn)
    data_vt = scrapertools.find_single_match(data_vt, 'jwConfig\|([^\|]+)\|')
    
    media_urls = scrapertools.find_multiple_matches(data,"label\s*\:\s*'([^']+)'\s*\,\s*file\s*\:\s*'([^']+)'")
    video_urls = []

    for label, media_url in media_urls:
        media_url += "?direct=false&ua=1&vt=%s" % data_vt
        video_urls.append( [ scrapertools.get_filename_from_url(media_url)[-4:]+" ("+label+") [thevideo.me]",media_url])

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    # Añade manualmente algunos erróneos para evitarlos
    encontrados = set()
    devuelve = []

    patronvideos = 'thevideo.me/(?:embed-)?([a-z0-9A-Z]+)'

    logger.info("streamondemand.servers.thevideome find_videos #" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    for match in matches:
        titulo = "[thevideo.me]"
        url = "http://thevideo.me/embed-" + match + ".html"
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'thevideome'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)
    return devuelve
