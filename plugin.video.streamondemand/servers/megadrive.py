# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para megadrive
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# by DrZ3r0
# ------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config
from core import jsunpack


# Returns an array of possible video url's from the page_url
def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[megadrive.py] get_video_url(page_url='%s')" % page_url)
    video_urls = []

    data = scrapertools.cache_page( page_url )
    media_url = scrapertools.get_match(data,'file: "([^"]+)",')
    video_urls = []
    video_urls.append( [ scrapertools.get_filename_from_url(media_url)[-3:]+" [megadrive]",media_url])

    return video_urls


# Encuentra videos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    patronvideos = r"""http://megadrive.tv/embed/([a-z0-9A-Z]+)"""
    logger.info("[megadrive.py] find_videos #" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    for match in matches:
        titulo = "[megadrive]"
        url = 'http://megadrive.tv/embed/%s' % match

        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'megadrive'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve
