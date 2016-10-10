# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para streaminto
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------

from core.scrapertools import *


def test_video_exists(page_url):
    logger.info("[streaminto.py] test_video_exists(page_url='%s')" % page_url)

    data = cache_page( url = page_url )
    if "File was deleted" in data:
        return False,"El archivo no existe en streaminto o ha sido borrado."
    else:
        return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("streamondemand.servers.streaminto url=" + page_url)

    data = re.sub( r'\n|\t|\s+', '', cache_page( page_url ) )

    video_urls = []
    media_url = get_match( data, """.setup\({file:"([^"]+)",image""" )
    video_urls.append( [ get_filename_from_url(media_url)[-4:] + " [streaminto]", media_url ] )

    for video_url in video_urls:
        logger.info("streamondemand.servers.streaminto %s - %s" % (video_url[0], video_url[1]))

    return video_urls


def find_videos(data):
    encontrados = set()
    devuelve = []

    # http://streamin.to/z3nnqbspjyne
    patronvideos  = 'streamin.to/?(?:embed\-|)([a-z0-9A-Z]+)'
    logger.info("[streaminto.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    for match in matches:
        titulo = "[streaminto]"
        url = "http://streamin.to/embed-"+match+"-640x360.html"
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'streaminto'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve
