# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para powvideo
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#------------------------------------------------------------

import re

from core import jsunpack
from core import logger
from core import scrapertools

headers = [['User-Agent','Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0']]


def test_video_exists( page_url ):
    logger.info("streamondemand.servers.powvideo test_video_exists(page_url='%s')" % page_url)
    
    data = scrapertools.cache_page(page_url)
    if "File Not Found" in data: return False, "[powvideo] El archivo no existe o  ha sido borrado"
    
    return True,""


def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("streamondemand.servers.powvideo get_video_url(page_url='%s')" % page_url)

    url = page_url.replace("http://powvideo.net/","http://powvideo.net/iframe-") + "-640x360.html"     
    headers.append(['Referer',url.replace("iframe","embed")])
    
    data = scrapertools.cache_page(url, headers=headers)

    # Extrae la URL
    data = scrapertools.find_single_match(data,"<script type='text/javascript'>(.*?)</script>")
    data = jsunpack.unpack(data).replace("\\","")

    data = scrapertools.find_single_match(data,"sources\=\[([^\]]+)\]")
    logger.info("data="+data)

    matches = scrapertools.find_multiple_matches(data, "src:'([^']+)'")
    video_urls = []
    for video_url in matches:
        filename = scrapertools.get_filename_from_url(video_url)[-4:]
        if video_url.startswith("rtmp"):
            rtmp, playpath = video_url.split("vod/",1)
            video_url = "%s playpath=%s swfUrl=http://powvideo.net/player6/jwplayer.flash.swf pageUrl=%s" % (rtmp+"vod/", playpath, page_url)
            filename = "RTMP"
        elif "m3u8" in video_url:
            video_url += "|User-Agent="+headers[0][1]

        video_urls.append( [ filename + " [powvideo]", video_url])

    for video_url in video_urls:
        logger.info("streamondemand.servers.powvideo %s - %s" % (video_url[0],video_url[1]))

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    # http://powvideo.net/sbb9ptsfqca2
    # http://powvideo.net/embed-sbb9ptsfqca2
    # http://powvideo.net/iframe-sbb9ptsfqca2
    # http://powvideo.net/preview-sbb9ptsfqca2
    patronvideos  = 'powvideo.net/(?:embed-|iframe-|preview-|)([a-z0-9]+)'
    logger.info("streamondemand.servers.powvideo find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[powvideo]"
        url = "http://powvideo.net/"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'powvideo' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
    return devuelve
