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
    logger.info("pelisalacarta.servers.openload test_video_exists(page_url='%s')" % page_url)

    data = scrapertools.downloadpageWithoutCookies(page_url)

    if 'We are sorry!' in data:
        return False, "[Openload] File cancellato o inesistente"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("pelisalacarta.servers.openload url=" + page_url)
    video_urls = []

    data = scrapertools.downloadpageWithoutCookies(page_url)
    subtitle = scrapertools.find_single_match(data, '<track kind="captions" src="([^"]+)" srclang="es"')
    # Header para la descarga
    header_down = "|User-Agent=" + headers['User-Agent']

    try:
        from lib.aadecode import decode as aadecode
        if "videocontainer" not in data:
            url = page_url.replace("/embed/", "/f/")
            data = scrapertools.downloadpageWithoutCookies(url)
            text_encode = scrapertools.find_multiple_matches(data, "(ﾟωﾟ.*?\(\'\_\'\));")
            text_decode = ""
            try:
                for t in text_encode:
                    text_decode += aadecode(t)
                videourl = "http://" + scrapertools.find_single_match(text_decode, '(openload.co/.*?)\}')
            except:
                videourl = "http://"

            if videourl == "http://":
                hiddenurl, valuehidden = scrapertools.find_single_match(data, '<span id="([^"]+)">(.*?)<')
                if hiddenurl:
                    number = scrapertools.find_single_match(text_decode, 'charCodeAt\(0\)\s*+\s*(\d+)')
                    if number:
                        videourl = decode_hidden(valuehidden, number)
                    else:
                        from jjdecode import JJDecoder
                        jjencode = scrapertools.find_single_match(data,
                                                                  '<script type="text/javascript">(j=.*?\(\)\)\(\);)')
                        if not jjencode:
                            pack = \
                            scrapertools.find_multiple_matches(data, '(eval \(function\(p,a,c,k,e,d\).*?\{\}\)\))')[-1]
                            jjencode = openload_clean(pack)

                        jjdec = JJDecoder(jjencode).decode()
                        number = scrapertools.find_single_match(jjdec, 'charCodeAt\(0\)\s*\+\s*(\d+)')
                        varj = scrapertools.find_single_match(jjdec, 'var j\s*=\s*(\w+)\.charCodeAt')
                        varhidden = scrapertools.find_single_match(jjdec,
                                                                   'var\s*' + varj + '\s*=\s*\$\("[#]*([^"]+)"\).text')
                        if varhidden != hiddenurl:
                            valuehidden = scrapertools.find_single_match(data, 'id="' + varhidden + '">(.*?)<')
                        videourl = decode_hidden(valuehidden, number)

                else:
                    videourl = decodeopenload(data)
            # Falla el método, se utiliza la api aunque en horas punta no funciona
            if not videourl:
                videourl = get_link_api(page_url)
        else:
            text_encode = scrapertools.find_multiple_matches(data, '(ﾟωﾟ.*?\(\'\_\'\));')
            text_decode = ""
            try:
                for t in text_encode:
                    text_decode += aadecode(t)
                subtract = scrapertools.find_single_match(text_decode, 'welikekodi.*?(\([^;]+\))')
            except:
                subtract = ""

            if subtract:
                index = int(eval(subtract))
                # Buscamos la variable que nos indica el script correcto
                text_decode2 = aadecode(text_encode[index])
                videourl = "https://" + scrapertools.find_single_match(text_decode2, "(openload.co/.*?)\}")
            else:
                hiddenurl, valuehidden = scrapertools.find_single_match(data, '<span id="([^"]+)">(.*?)<')
                if hiddenurl:
                    number = scrapertools.find_single_match(text_decode, 'charCodeAt\(0\)\s*+\s*(\d+)')
                    if number:
                        videourl = decode_hidden(valuehidden, number)
                    else:
                        from jjdecode import JJDecoder
                        jjencode = scrapertools.find_single_match(data,
                                                                  '<script type="text/javascript">(j=.*?\(\)\)\(\);)')
                        if not jjencode:
                            pack = \
                            scrapertools.find_multiple_matches(data, '(eval \(function\(p,a,c,k,e,d\).*?\{\}\)\))')[-1]
                            jjencode = openload_clean(pack)

                        jjdec = JJDecoder(jjencode).decode()
                        number = scrapertools.find_single_match(jjdec, 'charCodeAt\(0\)\s*\+\s*(\d+)')
                        varj = scrapertools.find_single_match(jjdec, 'var j\s*=\s*(\w+)\.charCodeAt')
                        varhidden = scrapertools.find_single_match(jjdec,
                                                                   'var\s*' + varj + '\s*=\s*\$\("[#]*([^"]+)"\).text')
                        if varhidden != hiddenurl:
                            valuehidden = scrapertools.find_single_match(data, 'id="' + varhidden + '">(.*?)<')
                        videourl = decode_hidden(valuehidden, number)
                else:
                    videourl = decodeopenload(data)

            # Falla el método, se utiliza la api aunque en horas punta no funciona
            if not videourl:
                videourl = get_link_api(page_url)
    except:
        import traceback
        logger.info("pelisalacarta.servers.openload " + traceback.format_exc())
        # Falla el método, se utiliza la api aunque en horas punta no funciona
        videourl = get_link_api(page_url)

    extension = scrapertools.find_single_match(data, '<meta name="description" content="([^"]+)"')
    extension = "." + extension.rsplit(".", 1)[1]
    if config.get_platform() != "plex":
        video_urls.append([extension + " [Openload] ", videourl + header_down + extension, 0, subtitle])
    else:
        video_urls.append([extension + " [Openload] ", videourl, 0, subtitle])

    for video_url in video_urls:
        logger.info("pelisalacarta.servers.openload %s - %s" % (video_url[0], video_url[1]))

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    patronvideos = '(?:openload|oload).../(?:embed|f)/([0-9a-zA-Z-_]+)'
    logger.info("pelisalacarta.servers.openload find_videos #" + patronvideos + "#")

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


# Code take from plugin IPTVPlayer: https://gitlab.com/iptvplayer-for-e2/iptvplayer-for-e2/
# Thanks to samsamsam for his work
def decodeopenload(data):
    import base64, math
    from lib.png import Reader as PNGReader
    # get image data
    imageData = scrapertools.find_single_match(data, '<img *id="linkimg" *src="([^"]+)"')

    imageData = base64.b64decode(imageData.rsplit('base64,', 1)[1])
    x, y, pixel, meta = PNGReader(bytes=imageData).read()

    imageStr = ""
    try:
        for item in pixel:
            for p in item:
                imageStr += chr(p)
    except:
        pass

    # split image data
    imageTabs = []
    i = -1
    for idx in range(len(imageStr)):
        if imageStr[idx] == '\0':
            break
        if 0 == (idx % (12 * 20)):
            imageTabs.append([])
            i += 1
            j = -1
        if 0 == (idx % (20)):
            imageTabs[i].append([])
            j += 1
        imageTabs[i][j].append(imageStr[idx])

    # get signature data
    signStr = ""
    try:
        data_obf = scrapertools.downloadpageWithoutCookies("https://openload.co/assets/js/obfuscator/n.js")
        if "signatureNumbers" in data_obf:
            signStr = scrapertools.find_single_match(data_obf, '[\'"]([^"\']+)[\'"]')
    except:
        pass

    if not signStr:
        scripts = scrapertools.find_multiple_matches(data, '<script src="(/assets/js/obfuscator/[^"]+)"')
        for scr in scripts:
            data_obf = scrapertools.downloadpageWithoutCookies('https://openload.co%s' % scr)
            if "signatureNumbers" in data_obf:
                signStr = scrapertools.find_single_match(data_obf, '[\'"]([^"\']+)[\'"]')
                break

    # split signature data
    signTabs = []
    i = -1
    for idx in range(len(signStr)):
        if signStr[idx] == '\0':
            break
        if 0 == (idx % (11 * 26)):
            signTabs.append([])
            i += 1
            j = -1
        if 0 == (idx % (26)):
            signTabs[i].append([])
            j += 1
        signTabs[i][j].append(signStr[idx])

    # get link data
    linkData = {}
    for i in [2, 3, 5, 7]:
        linkData[i] = []
        tmp = ord('c')
        for j in range(len(signTabs[i])):
            for k in range(len(signTabs[i][j])):
                if tmp > 122:
                    tmp = ord('b')
                if signTabs[i][j][k] == chr(int(math.floor(tmp))):
                    if len(linkData[i]) > j:
                        continue
                    tmp += 2.5;
                    if k < len(imageTabs[i][j]):
                        linkData[i].append(imageTabs[i][j][k])
    res = []
    for idx in linkData:
        res.append(''.join(linkData[idx]).replace(',', ''))

    res = res[3] + '~' + res[1] + '~' + res[2] + '~' + res[0]
    videourl = 'https://openload.co/stream/{0}?mime=true'.format(res)

    return videourl


def openload_clean(string):
    import urllib2
    if "function" in string:
        matches = re.findall(r"=\"([^\"]+).*?} *\((\d+)\)", string, re.DOTALL)[0]

        def substr(char):
            char = char.group(0)
            number = ord(char) + int(matches[1])
            if char <= "Z":
                char_value = 90
            else:
                char_value = 122
            if char_value >= number:
                return chr(ord(char))
            else:
                return chr(number - 26)

        string = re.sub(r"[A-Za-z]", substr, matches[0])
        string = urllib2.unquote(string)

        for n, z in enumerate(['j', '_', '__', '___']):
            string = re.sub(r'%s' % n, z, string)

    return string


def decode_hidden(text, number):
    text = scrapertools.decodeHtmlentities(text)
    text = text.replace("&gt9", ">").replace("&quot9", '"').replace("&lt9", '<').replace("&amp9", '&')
    s = []
    for char in text:
        j = ord(char)
        s.append(chr(33 + ((j + 14) % 94)))

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
    data = scrapertools.downloadpageWithoutCookies(
        "https://api.openload.co/1/file/dlticket?file=%s&login=%s&key=%s" % (file_id, login, key))
    data = jsontools.load_json(data)
    if data["status"] == 200:
        ticket = data["result"]["ticket"]
        data = scrapertools.downloadpageWithoutCookies(
            "https://api.openload.co/1/file/dl?file=%s&ticket=%s" % (file_id, ticket))
        data = jsontools.load_json(data)
        extension = "." + scrapertools.find_single_match(data["result"]["content_type"], '/(\w+)')
        videourl = data['result']['url']
        videourl = videourl.replace("https", "http")
        return videourl

    return ""