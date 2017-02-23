# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector for spruto.tv
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# by DrZ3r0
# ------------------------------------------------------------

import re

from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("streamondemand.servers.spruto test_video_exists(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)
    if "404.txt" in data:
        return False, "Il video è stato rimosso"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("streamondemand.servers.spruto url=" + page_url)

    data = scrapertools.cache_page(page_url)

    video_urls = []
    media_urls = scrapertools.find_multiple_matches(data, 'file":\s*"([^"]+)"')

    for media_url in media_urls:
        extension = scrapertools.get_filename_from_url(media_url)[-3:]
        if extension != "png" and extension != "php":
            video_urls.append([scrapertools.get_filename_from_url(media_url)[-4:] + " [spruto]", media_url])

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    patronvideos = [r'//(?:www.)?spruto.tv/iframe_embed.php\?video_id=(\d+)',
                    r'//(?:www.)?spruto.tv/videos/(\d+)']

    for patron in patronvideos:
        logger.info("[spruto.py] find_videos #" + patron + "#")

        matches = re.compile(patron, re.DOTALL).findall(text)

        for media_id in matches:
            titulo = "[spruto]"
            url = 'http://www.spruto.tv/iframe_embed.php?video_id=%s' % media_id
            if url not in encontrados:
                logger.info("  url=" + url)
                devuelve.append([titulo, url, 'spruto'])
                encontrados.add(url)
            else:
                logger.info("  url duplicada=" + url)

    return devuelve
