# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para gamovideo
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#------------------------------------------------------------

import re

from core import jsunpack
from core import logger
from core import scrapertools

headers = [["User-Agent","Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0"]]

def test_video_exists( page_url ):
    logger.info("streamondemand.servers.gamovideo test_video_exists(page_url='%s')" % page_url)
    data = scrapertools.cache_page(page_url, headers=headers)

    if ("File was deleted" or "Not Found") in data:
        return False, "[Gamovideo] El archivo no existe o ha sido borrado"

    return True, ""

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("streamondemand.servers.gamovideo get_video_url(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url,headers=headers)
    packer = scrapertools.find_single_match(data,"<script type='text/javascript'>(eval.function.p,a,c,k,e,d..*?)</script>")
    unpacker = jsunpack.unpack(data) if packer != "" else ""
    if unpacker != "": data = unpacker

    data = re.sub(r'\n|\t|\s+', '', data)

    host = scrapertools.get_match(data, '\[\{image:"(http://[^/]+/)')
    mediaurl = host+scrapertools.get_match(data, ',\{file:"([^"]+)"').split("=")[1]+"/v.flv"
   
    rtmp_url = scrapertools.get_match(data, 'file:"(rtmp[^"]+)"')
    playpath = scrapertools.get_match(rtmp_url, 'vod\?h=[\w]+/(.*$)')
    rtmp_url = rtmp_url.split(playpath)[0]+" playpath="+playpath+" swfUrl=http://gamovideo.com/player61/jwplayer.flash.swf"

    video_urls = []
    video_urls.append([scrapertools.get_filename_from_url(mediaurl)[-4:]+" [gamovideo]",mediaurl])
    video_urls.append(["RTMP [gamovideo]",rtmp_url])     

    for video_url in video_urls:
        logger.info("streamondemand.servers.gamovideo %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    # http://gamovideo.com/auoxxtvyoy
    # http://gamovideo.com/h1gvpjarjv88
    # http://gamovideo.com/embed-sbb9ptsfqca2-588x360.html
    patronvideos  = 'gamovideo.com/(?:embed-|)([a-z0-9]+)'
    logger.info("streamondemand.servers.gamovideo find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[gamovideo]"
        url = "http://gamovideo.com//embed-%s.html" % match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'gamovideo' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
           
    return devuelve
