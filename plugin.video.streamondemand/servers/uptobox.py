# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para uptobox
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#------------------------------------------------------------

import re
import urllib

from core import logger
from core import scrapertools


def test_video_exists( page_url ):
    logger.info("streamondemand.servers.uptobox test_video_exists(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)

    if "Streaming link:" in data: return True,""
    elif "Unfortunately, the file you want is not available." in data: return False, "[Uptobox] El archivo no existe o ha sido borrado"
    wait = scrapertools.find_single_match(data, "You have to wait ([0-9]+) (minute|second)")
    if len(wait)>0:
        tiempo = wait[1].replace("minute","minuto/s").replace("second","segundos")
        return False, "[Uptobox] Alcanzado límite de descarga.<br/>Tiempo de espera: "+wait[0]+" "+tiempo

    return True,""


def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("streamondemand.servers.uptobox get_video_url(page_url='%s')" % page_url)
    #Si el enlace es directo de upstream
    if "uptobox" not in page_url:
        data = scrapertools.cache_page(page_url)
        if "Video not found" in data:
            page_url = page_url.replace("uptostream.com/iframe/","uptobox.com/")
            data = scrapertools.cache_page(page_url)
            video_urls = uptobox(page_url, data)
        else:
            video_urls = uptostream(data)
    else:
        data = scrapertools.cache_page(page_url)
        #Si el archivo tiene enlace de streaming se redirige a upstream
        if "Streaming link:" in data:
            page_url = "http://uptostream.com/"+scrapertools.find_single_match(page_url,'uptobox.com/([a-z0-9]+)')
            data = scrapertools.cache_page(page_url)
            video_urls = uptostream(page_url)
        else:
            #Si no lo tiene se utiliza la descarga normal
            video_urls = uptobox(page_url, data)


    for video_url in video_urls:
        logger.info("streamondemand.servers.uptobox %s - %s" % (video_url[0],video_url[1]))
    return video_urls


def uptostream(data):
    video_urls = []
    patron = "<source src='//([^']+)' type='video/([^']+)' data-res='([^']+)'"
    media = scrapertools.find_multiple_matches(data, patron)
    for match in media:
        media_url = "http://"+match[0]
        extension = "."+match[1] + " ("+match[2]+")"
        video_urls.append( [ extension+" [uptostream]", media_url])
    
    video_urls.sort(reverse=True)   
    return video_urls


def uptobox(url, data):
    video_urls = []
    post = ""
    matches = scrapertools.find_multiple_matches(data, '<input type="hidden".*?name="([^"]+)".*?value="([^"]*)">')
    for inputname, inputvalue in matches:
        post += inputname + "=" + inputvalue + "&"

    data = scrapertools.cache_page(url, post=post)
    media = scrapertools.find_single_match(data, '<!--DOWNLOAD BUTTON-->[\s\S]+<a href="([^"]+)">')
    #Solo es necesario codificar la ultima parte de la url
    url_strip = urllib.quote(media.rsplit('/', 1)[1])
    media_url = media.rsplit('/', 1)[0] +"/"+url_strip
    extension = media_url[-4:]
    video_urls.append( [ extension+" [uptobox]", media_url])

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    # http://uptobox.com/q7asuktfr84x
    # http://uptostream.com/q7asuktfr84x
    # http://uptostream.com/iframe/q7asuktfr84x
    patronvideos  = '(?:uptobox|uptostream).com(?:/iframe/|/)([a-z0-9]+)'
    logger.info("streamondemand.servers.uptobox find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[uptobox]"
        if "uptostream" in data:
            url = "http://uptostream.com/iframe/"+match
        else:
            url = "http://uptobox.com/"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'uptobox' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve
