# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector for openload.co
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------

import re

from core import config
from core import logger
from core import scrapertools


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'}


def test_video_exists(page_url):
    logger.info("streamondemand.servers.openload test_video_exists(page_url='%s')" % page_url)

    data = scrapertools.downloadpageWithoutCookies(page_url)

    if 'We are sorry!' in data:
        return False, "[Openload] Il file non esiste o è stato rimosso" 

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("streamondemand.servers.openload url=" + page_url)
    video_urls = []

    data = scrapertools.downloadpageWithoutCookies(page_url)
    subtitle = scrapertools.find_single_match(data, '<track kind="captions" src="([^"]+)" srclang="it"')
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

        varj = scrapertools.find_single_match(text_decode, 'var\s*j\s*=\s*([A-z])')
        varhidden = scrapertools.find_single_match(text_decode, 'var\s*'+varj+'\s*=\s*\$\(\"[#]*([^"]+)"')
        valuehidden = scrapertools.find_single_match(data, 'id="'+varhidden+'">([^<]+)<')
        search_str = scrapertools.find_single_match(text_decode, 'var\s*str\s*=([^;]+)')
        funcnombres = scrapertools.find_multiple_matches(search_str, '[+-]\s*([_A-z0-9]+)\(\)')

        funciones = {}
        numbers = []
        for f in funcnombres:
            retorna = scrapertools.find_single_match(text_decode, f+'\(\)\s*\{.*?return\s*([^;]+)')
            if f in funciones:
                numbers.append(funciones[f])
                continue
            if not "()" in retorna:
                funciones[f] = eval(retorna)
            else:
                while "()" in retorna:
                    nuevafuncion = scrapertools.find_multiple_matches(retorna, '([_A-z0-9]+)\(\)')
                    for new in nuevafuncion:
                        if new in funciones:
                            retorna = retorna.replace(new+"()", str(funciones[new]))
                        else:
                            new2 = scrapertools.find_single_match(text_decode, new+'\(\)\s*\{.*?return\s*([^;]+)')
                            retorna = retorna.replace(new+"()", new2)
                funciones[f] = eval(retorna)
        
            numbers.append(funciones[f])

        videourl, extension = decode_hidden(valuehidden, numbers)

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


def decode_hidden(text, number):
    text = re.sub(r'(\&|\')(gt|lt|amp|anp)(9|;|:)', r'&\2;', text)
    text = text.replace("&anp;", "&").replace("&amq;", "&")
    text = scrapertools.decodeHtmlentities(text)
    s = []
    for char in text:
        j = ord(char)
        s.append(chr(33 + ((j+14) % 94)))

    temp = "".join(s)
    text_decode = temp[0:-number[0]] + chr(ord(temp[-number[1]]) + number[2]) + temp[len(temp)-number[3]+1:]
    videourl = "https://openload.co/stream/%s?mime=true" % text_decode
    resp_headers = scrapertools.get_headers_from_response(videourl)
    extension = ""
    for head, value in resp_headers:
        if head == "location":
            videourl = value.replace("https", "http").replace("?mime=true", "")
        elif head == "content-type":
            extension = value

    return videourl, extension


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
        extension = scrapertools.find_single_match(data["result"]["content_type"], '/(\w+)')
        videourl = data['result']['url']
        videourl = videourl.replace("https", "http")
        return videourl, extension

    return ""

