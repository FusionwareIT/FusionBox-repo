# -*- coding: iso-8859-1 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector for videowood.tv
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# by DrZ3r0
# ------------------------------------------------------------

import re
import urllib

from core import logger
from core import scrapertools
from lib.aadecode import decode as aadecode


def test_video_exists(page_url):
    logger.info("streamondemand.servers.videowood test_video_exists(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)

    if "This video doesn't exist." in data:
        return False, 'The requested video was not found.'

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("streamondemand.servers.videowood url=" + page_url)
    video_urls = []

    headers = [
        ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0'],
        ['Accept-Encoding', 'gzip, deflate'],
        ['Referer', page_url]
    ]

    data = scrapertools.cache_page(page_url, headers=headers)
    text_encode = scrapertools.find_single_match(data, "split\('\|'\)\)\)\s*(.*?)</script>")

    if text_encode:
        text_decode = aadecode(text_encode)

        # URL del video
        patron = "'([^']+)"
        media_url = scrapertools.find_single_match(text_decode, patron)

        video_urls.append([media_url[-4:] + " [Videowood]", media_url + '|' + urllib.urlencode(dict(headers))])

    return video_urls


# Encuentra videos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    patronvideos = '(?://|\.)videowood\.tv/(?:embed/|video/)([0-9a-zA-Z]+)'
    logger.info("streamondemand.servers.videowood find_videos #" + patronvideos + "#")

    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    for media_id in matches:
        titulo = "[Videowood]"
        url = 'http://videowood.tv/embed/%s' % media_id
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'videowood'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve
