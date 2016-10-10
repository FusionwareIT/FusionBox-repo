# -*- coding: iso-8859-1 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para VK Server
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------

import re

from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("streamondemand.servers.vk test_video_exists(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)

    if "This video has been removed from public access" in data:
        return False, "El archivo ya no esta disponible<br/>en VK (ha sido borrado)"
    else:
        return True, ""


# Returns an array of possible video url's from the page_url
def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("streamondemand.servers.vk get_video_url(page_url='%s')" % page_url)

    video_urls = []

    # Lee la página y extrae el ID del vídeo
    data = scrapertools.cache_page(page_url)

    try:
        patron = '<param name=.flashvars. value([^>]+)>'
        data = scrapertools.get_match(data, patron)
        patron = ';url([^\=]+)\=([^\&]+)\&'
    except:
        patron = 'var vars = {[^}]+}'
        data = scrapertools.get_match(data, patron).replace('\\/', '/')
        patron = '"url(\d+)":"([^"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(data)
    for calidad, media_url in matches:
        video_urls.append([scrapertools.get_filename_from_url(media_url)[-4:] + " [vk:" + calidad + "]", media_url])

    for video_url in video_urls:
        logger.info("streamondemand.servers.vk %s - %s" % (video_url[0], video_url[1]))

    return video_urls


def find_videos(data):
    encontrados = set()
    devuelve = []

    # http://vkontakte.ru/video_ext.php?oid=95855298&id=162902512&hash=4f0d023887f3648e
    # http://vk.com/video_ext.php?oid=70712020&amp;id=159787030&amp;hash=88899d94685174af&amp;hd=3"
    # http://vk.com/video_ext.php?oid=161288347&#038;id=162474656&#038;hash=3b4e73a2c282f9b4&#038;sd
    # http://vk.com/video_ext.php?oid=146263567&id=163818182&hash=2dafe3b87a4da653&sd
    # http://vk.com/video_ext.php?oid=146263567&id=163818182&hash=2dafe3b87a4da653
    # http://vk.com/video_ext.php?oid=-34450039&id=161977144&hash=0305047ffe3c55a8&hd=3
    data = data.replace("&amp;", "&")
    data = data.replace("&#038;", "&")
    patronvideos = '(/video_ext.php\?oid=[^&]+&id=[^&]+&hash=[a-z0-9]+)'
    logger.info("streamondemand.servers.vk find_videos #" + patronvideos + "#")
    matches = re.compile(patronvideos).findall(data)

    for match in matches:
        titulo = "[vk]"
        url = "http://vk.com" + match

        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'vk'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    # http://vk.com/video97482389_161509127?section=all
    patronvideos = '(vk\.[a-z]+\/video[0-9]+_[0-9]+)'
    logger.info("streamondemand.servers.vk find_videos #" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    for match in matches:
        titulo = "[vk]"
        url = "http ://" + match

        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'vk'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve
