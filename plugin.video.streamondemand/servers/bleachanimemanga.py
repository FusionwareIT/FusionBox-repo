# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# Server per bleachanimemanga
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------

import re
import urllib

from core import jsunpack
from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("bleachanimemanga test_video_exists(page_url='%s')" % page_url)
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("bleachanimemanga get_video_url(page_url='%s')" % page_url)
    patron_new_url = '<source\s+src\s*=\s*"([^"]+)'
    data = scrapertools.cache_page(page_url)
    logger.info("data="+data)

    video_urls = []

    patron  = '<source\s+src\s*=\s*"([^"]+)'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    print matches
    for match in matches:
        videourl = match
        logger.info(match)
        videourl = urllib.unquote(videourl)
        videourl = 'http://www.bleachanimemanga.org/' + videourl
        video_urls.append( [ "[bleachanimemanga]" , videourl ] )

    for video_url in video_urls:
        logger.info("[bleachanimemanga.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    print data
    encontrados = set()
    devuelve = []
    
    patronvideos = 'bleachanimemanga\.org\/sd\.php\?file=(.*)'
    logger.info("bleachanimemanga find_videos #" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    for media_id in matches:
        titulo = "[bleachanimemanga]"
        url = 'http://bleachanimemanga.org/sd.php?file=%s' % media_id
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'bleachanimemanga'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve
