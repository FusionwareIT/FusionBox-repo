# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector for openload.co by cmos
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand/
# ------------------------------------------------------------

import re

from core import config
from core import logger
from core import scrapertools


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'}


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = scrapertools.downloadpageWithoutCookies(page_url)

    if 'We’re Sorry!' in data:
        return False, "[Openload] File inesistente o eliminato" 

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []

    data = scrapertools.downloadpageWithoutCookies(page_url)
    subtitle = scrapertools.find_single_match(data, '<track kind="captions" src="([^"]+)" srclang="es"')
    #Header para la descarga
    header_down = "|User-Agent="+headers['User-Agent']

    try:
        from lib.aadecode import decode as aadecode
        if "videocontainer" not in data:
            url = page_url.replace("/embed/","/f/")
            data = scrapertools.downloadpageWithoutCookies(url)

        text_encode = scrapertools.find_multiple_matches(data, '(ﾟωﾟ.*?\(\'\_\'\));')
        text_decode = ""
        for t in text_encode:
            text_decode += aadecode(t)

        var_r = scrapertools.find_single_match(text_decode, "window.r\s*=\s*['\"]([^'\"]+)['\"]")
        var_encodes = scrapertools.find_multiple_matches(data, 'id="'+var_r+'[^"]*">([^<]+)<')

        videourl = ""
        text_decode = ""
        for encode in var_encodes:
            try:
                v1 = int(encode[0:3])
                v2 = int(encode[3:5])
                index = 5
                while index < len(encode):
                    text_decode += chr(int(encode[index:index+3]) + v1 - v2 * int(encode[index+3:index+3+2]))
                    index += 5
            except:
                continue
         
            videourl = "https://openload.co/stream/%s?mime=true" % text_decode
            resp_headers = scrapertools.get_headers_from_response(videourl)
            extension = ""
            for head, value in resp_headers:
                if head == "location":
                    videourl = value.replace("https", "http").replace("?mime=true", "")
                elif head == "content-type":
                    extension = value
            break

        # Falla el método, se utiliza la api aunque en horas punta no funciona
        if not videourl:
            videourl, extension = get_link_api(page_url)
    except:
        import traceback
        logger.info("streamondemand.servers.openload "+traceback.format_exc())
        # Falla el método, se utiliza la api aunque en horas punta no funciona
        videourl, extension = get_link_api(page_url)

    extension = extension.replace("video/", ".").replace("application/x-", ".")
    if not extension:
        try:
            extension = scrapertools.find_single_match(data, '<meta name="description" content="([^"]+)"')
            extension = "."+extension.rsplit(".", 1)[1]
        except:
            pass

    if config.get_platform() != "plex":
        video_urls.append([extension + " [Openload] ", videourl+header_down+extension, 0, subtitle])
    else:
        video_urls.append([extension + " [Openload] ", videourl, 0, subtitle])

    for video_url in video_urls:
        logger.info("streamondemand.servers.openload %s - %s" % (video_url[0],video_url[1]))

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    patronvideos = '(?:openload|oload).../(?:embed|f)/([0-9a-zA-Z-_]+)'
    logger.info("streamondemand.servers.openload find_videos #" + patronvideos + "#")

    matches = re.compile(patronvideos, re.DOTALL).findall(text)

    for media_id in matches:
        titulo = "[Openload]"
        url = 'https://openload.co/embed/%s/' % media_id
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'openload'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve


def get_link_api(page_url):
    from core import jsontools
    file_id = scrapertools.find_single_match(page_url, '(?:embed|f)/([0-9a-zA-Z-_]+)')
    login = "97b2326d7db81f0f"
    key = "AQFO3QJQ"
    data = scrapertools.downloadpageWithoutCookies("https://api.openload.co/1/file/dlticket?file=%s&login=%s&key=%s" % (file_id, login, key))
    data = jsontools.load_json(data)
    extension = ""
    if data["status"] == 200:
        ticket = data["result"]["ticket"]
        data = scrapertools.downloadpageWithoutCookies("https://api.openload.co/1/file/dl?file=%s&ticket=%s" % (file_id, ticket))
        data = jsontools.load_json(data)
        extension = data["result"]["content_type"]
        videourl = data['result']['url']
        videourl = videourl.replace("https", "http")
        return videourl, extension

    return ""

