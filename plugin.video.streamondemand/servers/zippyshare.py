# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para zippyshare
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#------------------------------------------------------------

import re

from core import logger
from core import scrapertools


def test_video_exists( page_url ):
    result = False
    message = ''

    try:
      error_message_file_not_exists = 'File does not exist on this server'
      error_message_file_deleted = 'File has expired and does not exist anymore on this server'
    
    
      headers=[]
      headers.append(["User-Agent",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:19.0) Gecko/20100101  Firefox/19.0"])

      data = scrapertools.cache_page(page_url,headers=headers)
    
      if error_message_file_not_exists in data:
          message = 'File does not exist.'
      elif error_message_file_deleted in data:
          message = 'File deleted.'
      else:
          result = True
    except Exception as ex:
        message = ex.message

    return result, message

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[zippyshare.py] get_video_url(page_url='%s')" % page_url)
    video_urls = []

    headers=[]
    headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:19.0) Gecko/20100101 Firefox/19.0"])

    data = scrapertools.cache_page(page_url,headers=headers)
    
    match = re.search('(.+)/v/(\w+)/file.html', page_url)
    domain = match.group(1)
    file_id = match.group(2)
    filename = re.search('\](.+)\[\/url\]', data).group(1)
    
    #Extract magic number
    pairs = re.findall('var \w = (\w|\d+) ([+-] \d+)', data)
    numbers = []
    for pair in pairs:
      numbers.extend(pair)
    del numbers[4]
    del numbers[2]
    
    magic_number = 0
    for number in numbers:
      magic_number += int(number)
        
    mediaurl = '%s/d/%s/%s/%s' % (domain, file_id, magic_number, filename)
    
    extension = mediaurl.split('.')[-1]
    
    video_urls.append( [ extension + " [zippyshare]", mediaurl ] )

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    #http://www5.zippyshare.com/v/11178679/file.html
    #http://www52.zippyshare.com/v/hPYzJSWA/file.html
    patronvideos  = '([a-z0-9]+\.zippyshare.com/v/[a-zA-Z0-9]+/file.html)'
    logger.info("[zippyshare.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[zippyshare]"
        url = "http://"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'zippyshare' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve
