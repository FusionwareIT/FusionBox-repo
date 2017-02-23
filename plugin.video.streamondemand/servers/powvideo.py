# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para powvideo
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#------------------------------------------------------------

import re

from core import jsunpack
from core import logger
from core import scrapertools

headers = [['User-Agent','Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0']]
host = "http://powvideo.net/"


def test_video_exists(page_url):
    logger.info("streamondemand.servers.powvideo test_video_exists(page_url='%s')" % page_url)
    
    data = scrapertools.cache_page(page_url)
    if "<title>watch </title>" in data.lower():
        return False, "[powvideo] El archivo no existe o  ha sido borrado"
    
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("streamondemand.servers.powvideo get_video_url(page_url='%s')" % page_url)

    url = page_url.replace(host, "http://powvideo.xyz/iframe-") + "-954x562.html"
    headers.append(['Referer', url.replace("iframe","preview")])
    
    data = scrapertools.cache_page(url, headers=headers)

    jj_encode = scrapertools.find_single_match(data, "(\w+=~\[\];.*?\)\(\)\)\(\);)")
    jj_decode = None
    jj_patron = None
    reverse = False
    substring = False
    splice = False
    if jj_encode:
        jj_decode = jjdecode(jj_encode)
    if jj_decode:
        jj_patron = scrapertools.find_single_match(jj_decode, "/([^/]+)/")
    if not "(" in jj_patron: jj_patron = "(" + jj_patron
    if not ")" in jj_patron: jj_patron += ")"

    if "x72x65x76x65x72x73x65" in jj_decode: reverse = True
    if "x73x75x62x73x74x72x69x6Ex67" in jj_decode: substring = True
    if "x73x70x6Cx69x63x65" in jj_decode: splice = True

    matches = scrapertools.find_single_match(data, "<script type=[\"']text/javascript[\"']>(eval.*?)</script>")
    data = jsunpack.unpack(data).replace("\\", "")

    data = scrapertools.find_single_match(data.replace('"', "'"), "sources\s*=[^\[]*\[([^\]]+)\]")
    matches = scrapertools.find_multiple_matches(data, "[src|file]:'([^']+)'")
    video_urls = []
    for video_url in matches:
        _hash = scrapertools.find_single_match(video_url, '\w{40,}')
        if splice:
            splice = int(scrapertools.find_single_match(jj_decode, "\((\d),\d\);"))
            if reverse:
                h = list(_hash)
                h.pop(-splice-1)
                _hash = "".join(h)
            else:
                h = list(_hash)
                h.pop(splice)
                _hash = "".join(h)
        if substring:
            substring = int(scrapertools.find_single_match(jj_decode, "_\w+.\d...(\d)...;"))
            if reverse:
                _hash = _hash[:-substring]
            else:
                _hash = _hash[substring:]
        if reverse:
            video_url = re.sub(r'\w{40,}', _hash[::-1], video_url)
        filename = scrapertools.get_filename_from_url(video_url)[-4:]
        if video_url.startswith("rtmp"):
            rtmp, playpath = video_url.split("vod/", 1)
            video_url = "%s playpath=%s swfUrl=%splayer6/jwplayer.flash.swf pageUrl=%s" % (rtmp + "vod/", playpath, host, page_url)
            filename = "RTMP"
        elif video_url.endswith(".m3u8"):
            video_url += "|User-Agent=" + headers[0][1]
        elif video_url.endswith("/v.mp4"):
            video_url_flv = re.sub(r'/v.mp4$','/v.flv',video_url)
            video_urls.append( [ ".flv" + " [powvideo]", re.sub(r'%s' % jj_patron, r'\1', video_url_flv)])

        video_urls.append([filename + " [powvideo]", re.sub(r'%s' % jj_patron, r'\1', video_url)])

    video_urls.sort(key=lambda x:x[0], reverse=True)
    for video_url in video_urls:
        logger.info("streamondemand.servers.powvideo %s - %s" % (video_url[0], video_url[1]))

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    # http://powvideo.net/sbb9ptsfqca2
    # http://powvideo.net/embed-sbb9ptsfqca2
    # http://powvideo.net/iframe-sbb9ptsfqca2
    # http://powvideo.net/preview-sbb9ptsfqca2
    patronvideos = 'powvideo.net/(?:embed-|iframe-|preview-|)([a-z0-9]+)'
    logger.info("streamondemand.servers.powvideo find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[powvideo]"
        url = "http://powvideo.net/"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append([titulo, url, 'powvideo' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
    return devuelve


def jjdecode(t):

    x = '0123456789abcdef'
    j = scrapertools.get_match(t, '^([^=]+)=')
    t = t.replace(j + '.', 'j.')

    t = re.sub(r'^.*?"\\""\+(.*?)\+"\\"".*?$', r'\1', t.replace('\\\\', '\\')) + '+""'
    t = re.sub('(\(!\[\]\+""\)\[j\._\$_\])', '"l"', t)
    t = re.sub(r'j\._\$\+', '"o"+', t)
    t = re.sub(r'j\.__\+', '"t"+', t)
    t = re.sub(r'j\._\+', '"u"+', t)

    p = scrapertools.find_multiple_matches(t, '(j\.[^\+]+\+)')
    for c in p:
        t = t.replace(c, c.replace('_', '0').replace('$', '1'))

    p = scrapertools.find_multiple_matches(t, 'j\.(\d{4})')
    for c in p:
        t = re.sub(r'j\.%s' % c, '"' + x[int(c, 2)] + '"', t)

    p = scrapertools.find_multiple_matches(t, '\\"\+j\.(001)\+j\.(\d{3})\+j\.(\d{3})\+')
    for c in p:
        t = re.sub(r'\\"\+j\.%s\+j\.%s\+j\.%s\+' % (c[0], c[1], c[2]), chr(int("".join(c), 2)) + '"+', t)

    p = scrapertools.find_multiple_matches(t, '\\"\+j\.(\d{3})\+j\.(\d{3})\+')
    for c in p:
        t = re.sub(r'\\"\+j\.%s\+j\.%s\+' % (c[0], c[1]), chr(int("".join(c),2)) + '"+', t)

    p = scrapertools.find_multiple_matches(t, 'j\.(\d{3})')
    for c in p:
        t = re.sub(r'j\.%s' % c, '"' + str(int(c, 2)) + '"', t)

    r = re.sub(r'"\+"|\\\\','',t[1:-1])

    return r
