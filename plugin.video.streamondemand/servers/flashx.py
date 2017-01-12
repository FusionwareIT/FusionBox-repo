# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para flashx - by smytvshow
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------

import re
import os

from core import scrapertools
from core import logger
from core import jsunpack
import base64 as b64

import urllib, time


def test_video_exists(page_url):
    logger.info("streamondemand.servers.flashx test_video_exists(page_url='%s')" % page_url)

    data = scrapertools.downloadpageWithoutCookies(page_url.replace("playvid-", ""))

    if 'File Not Found' in data:
        return False, "[FlashX] File assente o eliminato"
    elif 'Video is processing now' in data:
        return False, "[FlashX] File processato"

    return True, ""


def http_head(head):
    headers = []

    patron = "-H '([^\:]+): (.*?)'"
    matches = re.compile(patron, re.DOTALL).findall(head)
    for h, c in matches:
        headers.append([h, c])

    return headers

def find_videos(data):
    # Añade manualmente algunos erróneos para evitarlos
    encontrados = set()
    devuelve = []

    # http://flashx.tv/z3nnqbspjyne
    # http://www.flashx.tv/embed-li5ydvxhg514.html
    patronvideos = 'flashx.(?:tv|pw)/(?:embed.php\?c=|embed-|playvid-|)([A-z0-9]+)'
    logger.info("streamondemand.servers.flashx find_videos #" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    for match in matches:
        titulo = "[flashx]"
        url = "https://www.flashx.tv/playvid-%s.html" % match
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'flashx'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve

def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    # Lo pide una vez
    cookies = ""
    fileContainer = ""
    '''
    data = scrapertools.cache_page(page_url)
    # Si salta aviso, se carga la pagina de comprobacion y luego la inicial
    if "You try to access this video with Kodi" in data:

        url_reload = scrapertools.find_single_match(data, 'try to reload the page.*?href="([^"]+)"')
        url_reload = "http://www.flashx.tv" + url_reload[1:]
        try:
            data = scrapertools.cache_page(url_reload, headers=headers)
            data = scrapertools.cache_page(page_url, headers=headers)
        except:
            pass

    patron = "<script type='text/javascript'>(.*?)</script>"
    jsfiles = re.compile(patron, re.DOTALL).findall(data)
    for jsfile in jsfiles:
        if jsfile.startswith("eval"):
            try:
                m = jsunpack.unpack(jsfile)
                #fake = (scrapertools.find_single_match(m, "(\w{40,})") == "")
                fake = True
                if fake:
                    pass
                else:
                    fileContainer += m
                    break
            except:
                pass
    '''
    if fileContainer == "":
        page_url = page_url.replace("playvid-", "")

        head = "-H 'Host: www.flashx.tv' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.5' -H 'Accept-Encoding: gzip, deflate, br' -H 'Connection: keep-alive' -H 'Upgrade-Insecure-Requests: 1'"
        headers = http_head(head)
        headers.append(['Cookie', cookies[:-1]])
        data = scrapertools.downloadpage(page_url, headers=headers)

        b64_id = ""
        patron = "'file_id', '(.*?)'"
        matches = re.compile(patron, re.DOTALL).findall(data)
        for id in matches:
            b64_id = b64.encodestring(id)

        flashx_id = scrapertools.find_single_match(data, 'name="id" value="([^"]+)"')
        fname = scrapertools.find_single_match(data, 'name="fname" value="([^"]+)"')
        hash_f = scrapertools.find_single_match(data, 'name="hash" value="([^"]+)"')
        wait_time = scrapertools.find_single_match(data, "<span id='xxc2'>(\d+)")

        page_url = 'https://files.fx.fastcontentdelivery.com/jquery2.js?fx=%s' % b64_id
        head = "-H 'Host: files.fx.fastcontentdelivery.com' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36' -H 'Accept: */*' -H 'Accept-Language: en-US,en;q=0.5' -H 'Accept-Encoding: gzip, deflate, br' -H 'Referer: https://www.flashx.tv/' -H 'Connection: keep-alive'"
        headers = http_head(head)
        headers.append(['Cookie', cookies[:-1]])
        scrapertools.downloadpage(page_url, headers=headers)

        page_url = 'https://www.flashx.tv/counter.cgi?fx=%s' % b64_id
        head = "-H 'Accept: */*' -H 'Accept-Encoding: gzip, deflate, br' -H 'Accept-Language: en-US,en;q=0.5' -H 'Connection: keep-alive' -H 'Host: www.flashx.tv' -H 'Referer: https://www.flashx.tv/' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36'"
        headers = http_head(head)
        headers.append(['Cookie', cookies[:-1]])
        scrapertools.downloadpage(page_url, headers=headers)

        page_url = 'https://www.flashx.tv/flashx.php?fxfx=3'
        head = "-H 'Host: www.flashx.tv' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36' -H 'Accept: */*' -H 'Accept-Language: en-US,en;q=0.5' -H 'Accept-Encoding: gzip, deflate, br' -H 'X-Requested-With: XMLHttpRequest' -H 'Referer: https://www.flashx.tv/' -H 'Connection: keep-alive'"
        headers = http_head(head)
        headers.append(['Cookie', cookies[:-1]])
        scrapertools.downloadpage(page_url, headers=headers)

        try:
            time.sleep(int(wait_time) + 1)
        except:
            time.sleep(6)

        url = 'https://www.flashx.tv/dl?playthis'
        head = "-H 'Host: www.flashx.tv' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.5' -H 'Accept-Encoding: gzip, deflate, br' -H 'Referer: https://www.flashx.tv/' -H 'Connection: keep-alive' -H 'Upgrade-Insecure-Requests: 1' -H 'Content-Type: application/x-www-form-urlencoded'"
        headers = http_head(head)
        headers.append(['Cookie', cookies[:-1]])
        post = \
            'op=%s' \
            '&usr_login=%s' \
            '&id=%s' \
            '&fname=%s' \
            '&referer=%s' \
            '&hash=%s' \
            '&imhuman=%s' % \
            (
                "download1",
                "",
                flashx_id,
                urllib.quote(fname),
                '',
                hash_f,
                "Proceed+to+video"
            )
        data = scrapertools.downloadpage(url, post=post, headers=headers)
        patron = "<script type='text\/javascript'>(eval\(function\(p,a,c,k,e,d\).*?)\s+</script>"
        jsfiles = re.compile(patron, re.DOTALL).findall(data)
        for jsfile in jsfiles:
            try:
                m = jsunpack.unpack(jsfile)
                if "vplayer1" in m:
                    fileContainer += m
            except:
                pass

    video_urls = []

    patron = '\{file\:"([^"]+)",label:"([^"]+)"'
    media_urls = re.compile(patron, re.DOTALL).findall(fileContainer)

    for media_url, label in media_urls:
        if not media_url.endswith("png") and not media_url.endswith(".srt"):
            video_urls.append([label, media_url])

    return video_urls

