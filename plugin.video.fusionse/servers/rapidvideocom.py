# -*- coding: iso-8859-1 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para rapidvideo
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------
import random
import re
import urllib

from core import logger
from core import scrapertools
from lib.aadecode import decode as aadecode


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[rapidvideocom.py] url=" + page_url)
    video_urls = []

    headers = [
        ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0'],
        ['Accept-Encoding', 'gzip, deflate'],
        ['Referer', page_url]
    ]

    html = scrapertools.cache_page(page_url, headers=headers)

    data = get_hidden(html)
    data['confirm.y'] = random.randint(0, 120)
    data['confirm.x'] = random.randint(0, 120)

    post_url = page_url + '#'

    html = scrapertools.cache_page(post_url, post=urllib.urlencode(data), headers=headers)

    match = re.search('(....ωﾟ.*?);</script>', html, re.DOTALL)
    if match:
        html = aadecode(match.group(1))

    match = re.search('"?sources"?\s*:\s*\[(.*?)\]', html, re.DOTALL)
    if match:
        for match in re.finditer('''['"]?file['"]?\s*:\s*['"]([^'"]+)['"][^}]*['"]?label['"]?\s*:\s*['"]([^'"]*)''', match.group(1), re.DOTALL):
            media_url, _label = match.groups()
            media_url = media_url.replace('\/', '/')

            video_urls.append([_label + " [rapidvideocom]", media_url + '|' + urllib.urlencode(dict(headers))])

    return video_urls


# Encuentra vídeos de este servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    # http://www.rapidvideo.org/ttsvqng2qp2v/Scooby-Doo_e_la_Maschera_di_Blue_Falcon_720p.mp4.html
    patronvideos = '(?://|\.)(?:rapidvideo\.com)/(?:embed/|\?v=)?([0-9A-Za-z]+)'
    logger.info("[rapidvideocom.py] find_videos #" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).findall(text)

    for match in matches:
        titulo = "[rapidvideocom]"
        url = 'https://www.rapidvideo.com/embed/%s' % match
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'rapidvideocom'])

            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve


def get_hidden(html, form_id=None):
    hidden = {}
    if form_id:
        pattern = '''<form [^>]*id\s*=\s*['"]?%s['"]?[^>]*>(.*?)</form>'''
    else:
        pattern = '''<form[^>]*>(.*?)</form>'''

    for form in re.finditer(pattern, html, re.DOTALL | re.I):
        for field in re.finditer('''<input [^>]*type=['"]?hidden['"]?[^>]*>''', form.group(1)):
            match = re.search('''name\s*=\s*['"]([^'"]+)''', field.group(0))
            match1 = re.search('''value\s*=\s*['"]([^'"]*)''', field.group(0))
            if match and match1:
                hidden[match.group(1)] = match1.group(1)

    logger.info('Hidden fields are: %s' % hidden)
    return hidden
