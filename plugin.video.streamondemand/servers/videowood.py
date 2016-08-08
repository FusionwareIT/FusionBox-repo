# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector for videowood.tv
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# by DrZ3r0
# ------------------------------------------------------------

import re

from core import logger
from core import scrapertools


def decode(data):
    parse = re.search('(....ωﾟ.*?);</script>', data)
    if parse:
        todecode = parse.group(1).split(';')
        todecode = todecode[-1].replace(' ', '')

        code = {
            "(ﾟДﾟ)[ﾟoﾟ]": "o",
            "(ﾟДﾟ) [return]": "\\",
            "(ﾟДﾟ) [ ﾟΘﾟ]": "_",
            "(ﾟДﾟ) [ ﾟΘﾟﾉ]": "b",
            "(ﾟДﾟ) [ﾟｰﾟﾉ]": "d",
            "(ﾟДﾟ)[ﾟεﾟ]": "/",
            "(oﾟｰﾟo)": '(u)',
            "3ﾟｰﾟ3": "u",
            "(c^_^o)": "0",
            "(o^_^o)": "3",
            "ﾟεﾟ": "return",
            "ﾟωﾟﾉ": "undefined",
            "_": "3",
            "(ﾟДﾟ)['0']": "c",
            "c": "0",
            "(ﾟΘﾟ)": "1",
            "o": "3",
            "(ﾟｰﾟ)": "4",
        }
        cryptnumbers = []
        for searchword, isword in code.iteritems():
            todecode = todecode.replace(searchword, isword)
        for i in range(len(todecode)):
            if todecode[i:i + 2] == '/+':
                for j in range(i + 2, len(todecode)):
                    if todecode[j:j + 2] == '+/':
                        cryptnumbers.append(todecode[i + 1:j])
                        break
        finalstring = ''
        for item in cryptnumbers:
            chrnumber = '\\'
            jcounter = 0
            while jcounter < len(item):
                clipcounter = 0
                if item[jcounter] == '(':
                    jcounter += 1
                    clipcounter += 1
                    for k in range(jcounter, len(item)):
                        if item[k] == '(':
                            clipcounter += 1
                        elif item[k] == ')':
                            clipcounter -= 1
                        if clipcounter == 0:
                            jcounter = 0
                            chrnumber += str(eval(item[:k + 1]))
                            item = item[k + 1:]
                            break
                else:
                    jcounter += 1
            finalstring += chrnumber.decode('unicode-escape')
        stream_url = re.search('=\s*(\'|")(.*?)$', finalstring)
        if stream_url:
            return stream_url.group(2)
    else:
        return


def test_video_exists(page_url):
    logger.info("[videowood.py] test_video_exists(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)

    if "This video doesn't exist." in data:
        return False, 'The requested video was not found.'

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[videowood.py] url=" + page_url)
    video_urls = []

    data = scrapertools.cache_page(page_url)

    url = decode(data)
    video_urls.append([".mp4" + " [Videowood]", url])

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    patronvideos = r"https?://(?:www.)?videowood.tv/(?:embed/|video/)[0-9a-z]+"
    logger.info("[videowood.py] find_videos #" + patronvideos + "#")

    matches = re.compile(patronvideos, re.DOTALL).findall(text)

    for url in matches:
        titulo = "[Videowood]"
        url = url.replace('/video/', '/embed/')
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'videowood'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve
