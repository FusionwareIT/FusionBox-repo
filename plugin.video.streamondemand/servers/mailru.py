# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para mail.ru
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#------------------------------------------------------------

import re

from core import jsontools
from core import logger
from core import scrapertools

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[mailru.py] get_video_url(page_url='%s')" % (page_url))

    video_urls = []
    ## Carga la página para coger las cookies
    data = scrapertools.cache_page(page_url)

    ## Nueva url
    url = page_url.replace("embed/","").replace(".html",".json")
    ## Carga los datos y los headers
    data, headers = scrapertools.read_body_and_headers(url)
    data = jsontools.load_json( data )

    ## La cookie video_key necesaria para poder visonar el video
    for cookie in headers:
        if 'set-cookie' in cookie: break
    cookie_video_key = scrapertools.get_match(cookie[1], '(video_key=[a-f0-9]+)')

    ## Formar url del video + cookie video_key
    for videos in data['videos']:
        media_url = videos['url'] + "|Cookie=" + cookie_video_key
        quality = " "+videos['key']
        video_urls.append( [ scrapertools.get_filename_from_url(media_url)[-4:] + quality +" [mail.ru]", media_url ] )

    for video_url in video_urls:
        logger.info("[mail.ru] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    logger.info("[mailru.py] find_videos")
    encontrados = set()
    devuelve = []

    # http://videoapi.my.mail.ru/videos/embed/mail/bartos1100/_myvideo/1136.html
    patronvideos  = 'videoapi.my.mail.ru/videos/embed/(mail|inbox)/([\w]+)/_myvideo/(\d+).html'
    logger.info("[mailru.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[mail.ru]"
        url = "http://videoapi.my.mail.ru/videos/embed/"+match[0]+"/"+match[1]+"/_myvideo/"+match[2]+".html"
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'mailru' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve
