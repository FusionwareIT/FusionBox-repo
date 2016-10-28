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
        return False, "[Openload] File non presente o cancellato" 

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("streamondemand.servers.openload url=" + page_url)
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
            text_encode = scrapertools.find_multiple_matches(data,"(ﾟωﾟ.*?\(\'\_\'\));")
            text_decode = ""
            for t in text_encode:
                text_decode += aadecode(t)

            number = scrapertools.find_single_match(text_decode, 'charCodeAt\(0\)\s*\+\s*(\d+)')
            varj = scrapertools.find_single_match(text_decode, 'var magic\s*=\s*(\w+)\.slice')
            varhidden = scrapertools.find_single_match(text_decode, 'var\s*'+varj+'\s*=\s*\$\("[#]*([^"]+)"\).text')
            valuehidden = scrapertools.find_single_match(data, 'id="'+varhidden+'">(.*?)<')
            magic = ord(valuehidden[-1])
            valuehidden = valuehidden.split(chr(magic-1))
            valuehidden = "\t".join(valuehidden)
            valuehidden = valuehidden.split(valuehidden[-1])
            valuehidden = chr(magic-1).join(valuehidden)
            valuehidden = valuehidden.split("\t")
            valuehidden = chr(magic).join(valuehidden)
            
            videourl = decode_hidden(valuehidden, number)
            # Falla el método, se utiliza la api aunque en horas punta no funciona
            if not videourl:
                videourl = get_link_api(page_url)
        else:
            text_encode = scrapertools.find_multiple_matches(data, '(ﾟωﾟ.*?\(\'\_\'\));')
            text_decode = ""
            for t in text_encode:
                text_decode += aadecode(t)

            number = scrapertools.find_single_match(text_decode, 'charCodeAt\(0\)\s*\+\s*(\d+)')
            varj = scrapertools.find_single_match(text_decode, 'var magic\s*=\s*(\w+)\.slice')
            varhidden = scrapertools.find_single_match(text_decode, 'var\s*'+varj+'\s*=\s*\$\("[#]*([^"]+)"\).text')
            valuehidden = scrapertools.find_single_match(data, 'id="'+varhidden+'">(.*?)<')
            magic = ord(valuehidden[-1])
            valuehidden = valuehidden.split(chr(magic-1))
            valuehidden = "\t".join(valuehidden)
            valuehidden = valuehidden.split(valuehidden[-1])
            valuehidden = chr(magic-1).join(valuehidden)
            valuehidden = valuehidden.split("\t")
            valuehidden = chr(magic).join(valuehidden)
            
            videourl = decode_hidden(valuehidden, number)

            # Falla el método, se utiliza la api aunque en horas punta no funciona
            if not videourl:
                videourl = get_link_api(page_url)
    except:
        import traceback
        logger.info("streamondemand.servers.openload "+traceback.format_exc())
        # Falla el método, se utiliza la api aunque en horas punta no funciona
        videourl = get_link_api(page_url)

    extension = scrapertools.find_single_match(data, '<meta name="description" content="([^"]+)"')
    extension = "." + extension.rsplit(".", 1)[1]
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


def openload_clean(string):
    import urllib2
    if "function" in string:
        a, z = scrapertools.get_match(string,r"=\"([^\"]+).*?} *\((\d+)\)")

        x = scrapertools.find_multiple_matches(a, '([a-zA-Z])')

        for c in x:
            y = (32 | ord(c)) + int(z)
            x = chr(y) if 122 >= y else chr(y-26)
            a = re.sub(r'(%s)' % c, x , a)

        string = urllib2.unquote(a)

        for n, c in enumerate(['j','_','__','___']):
            string = re.sub(r'%s' % n, c, string)

    return string


def decode_hidden(text, number):
    text = scrapertools.decodeHtmlentities(text)
    text = text.replace("&gt9", ">").replace("&quot9", '"').replace("&lt9", '<').replace("&amp9", '&')
    s = []
    for char in text:
        j = ord(char)
        s.append(chr(33 + ((j+14) % 94)))

    temp = "".join(s)
    text_decode = temp[0:-1] + chr(ord(temp[-1]) + int(number))
    videourl = "https://openload.co/stream/{0}?mime=true".format(text_decode)
    videourl = scrapertools.getLocationHeaderFromResponse(videourl)
    videourl = videourl.replace("https", "http").replace("?mime=true", "")

    return videourl


def get_link_api(page_url):
    from core import jsontools
    file_id = scrapertools.find_single_match(page_url, 'embed/([0-9a-zA-Z-_]+)')
    login = "97b2326d7db81f0f"
    key = "AQFO3QJQ"
    data = scrapertools.downloadpageWithoutCookies("https://api.openload.co/1/file/dlticket?file=%s&login=%s&key=%s" % (file_id, login, key))
    data = jsontools.load_json(data)
    if data["status"] == 200:
        ticket = data["result"]["ticket"]
        data = scrapertools.downloadpageWithoutCookies("https://api.openload.co/1/file/dl?file=%s&ticket=%s" % (file_id, ticket))
        data = jsontools.load_json(data)
        extension = "." + scrapertools.find_single_match(data["result"]["content_type"], '/(\w+)')
        videourl = data['result']['url']
        videourl = videourl.replace("https", "http")
        return videourl

    return ""

