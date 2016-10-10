# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Sito hdgratis.org  by SchisM
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------
import base64
import re
import urlparse

from core import config
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "hdgratis"
__category__ = "F,S,A"
__type__ = "generic"
__title__ = "HDGratis"
__language__ = "IT"

host = "http://altadefinizione.black"

headers = [
    ['User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0'],
    ['Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', host],
    ['Cache-Control', 'max-age=0']
]


def isGeneric():
    return True


def mainlist(item):
    logger.info("[hdgratis.py] mainlist")

    itemlist = [
        Item(channel=__channel__,
             title="[COLOR azure]Ultimi Film Inseriti[/COLOR]",
             action="fichas",
             url=host + "/nuove-uscite/",
             thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),

        Item(channel=__channel__,
             title="[COLOR azure]Al Cinema[/COLOR]",
             action="fichas",
             url=host + "/al-cinema/",
             thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),

        Item(channel=__channel__,
             title="[COLOR azure]Film per Genere[/COLOR]",
             action="genere",
             url=host,
             thumbnail=""),

        Item(channel=__channel__,
             title="[COLOR azure]Film Sub-Ita[/COLOR]",
             action="fichas",
             url=host + "/sub-ita/",
             thumbnail="http://i.imgur.com/qUENzxl.png"),

        Item(channel=__channel__,
             title="[COLOR orange]Cerca...[/COLOR]",
             action="search",
             extra="movie",
             thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist


def search(item, texto):
    logger.info("[hdgratis.py] " + item.url + " search " + texto)

    item.url = host + "/?s=" + texto

    try:
        return fichas(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def genere(item):
    logger.info("[hdgratis.py] genere")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers)

    patron = '<ul class="listSubCat" id="Film">(.*?)</ul>'

    data = scrapertools.find_single_match(data, patron)

    patron = '<li><a href="(.*?)">(.*?)</a></li>'

    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="fichas",
                 title=scrapedtitle,
                 url=scrapedurl,
                 folder=True))

    return itemlist




def fichas(item):
    logger.info("[hdgratis.py] fichas")

    itemlist = []

    # Descarga la pagina
    data = scrapertools.anti_cloudflare(item.url, headers)
    # fix - calidad

    # ------------------------------------------------
    cookies = ""
    matches = re.compile('(.altadefinizione.black.*?)\n', re.DOTALL).findall(config.get_cookie_data())
    for cookie in matches:
        name = cookie.split('\t')[5]
        value = cookie.split('\t')[6]
        cookies += name + "=" + value + ";"
    headers.append(['Cookie', cookies[:-1]])
    import urllib
    _headers = urllib.urlencode(dict(headers))
    # ------------------------------------------------

    if "/?s=" in item.url:
        patron = '<div class="col-lg-3 col-md-3 col-xs-3">\s*<a href="([^"]+")>\s*<div class="wrapperImage">[^i]+i[^s]+src="([^"]+)"[^>]+> <div class="info">\s*<h5[^>]+>(.*?)<'
    else:
        patron = '<span class="hd">HD</span>\s*<a href="([^"]+)"><img[^s]+src="([^"]+)"[^>]+></a> <div class="info">\s*<[^>]+>[^>]+>(.*?)</a>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle  in matches:

        title = scrapertools.decodeHtmlentities(scrapedtitle)

        # ------------------------------------------------
        scrapedthumbnail += "|" + _headers
        # ------------------------------------------------

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 title=title,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=title,
                 show=scrapedtitle), tipo='movie'))

    # Paginación
    next_page = re.compile('<link rel="next" href="(.+?)"/>', re.DOTALL).findall(data)
    for page in next_page:
        next_page = page

    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="fichas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=next_page,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png"))

    return itemlist


def findvideos(item):
    logger.info("[hdgratis.py] findvideos")

    # Descarga la página
    data = scrapertools.anti_cloudflare(item.url, headers).replace('\n', '')

    patron = r'<iframe width=".+?" height=".+?" src="([^"]+)"></iframe>'
    url = scrapertools.find_single_match(data, patron).replace("?alta", "")
    url = url.replace("&download=1", "")

    if 'hdpass' in url:
        data = scrapertools.cache_page(url, headers=headers)

        start = data.find('<div class="row mobileRes">')
        end = data.find('<div id="playerFront">', start)
        data = data[start:end]

        patron_res = '<div class="row mobileRes">(.*?)</div>'
        patron_mir = '<div class="row mobileMirrs">(.*?)</div>'
        patron_media = r'<input type="hidden" name="urlEmbed" data-mirror="([^"]+)" id="urlEmbed" value="([^"]+)"/>'

        res = scrapertools.find_single_match(data, patron_res)

        urls = []
        for res_url, res_video in scrapertools.find_multiple_matches(res, '<option.*?value="([^"]+?)">([^<]+?)</option>'):

            data = scrapertools.cache_page(urlparse.urljoin(url, res_url), headers=headers).replace('\n', '')

            mir = scrapertools.find_single_match(data, patron_mir)

            for mir_url in scrapertools.find_multiple_matches(mir, '<option.*?value="([^"]+?)">[^<]+?</value>'):

                data = scrapertools.cache_page(urlparse.urljoin(url, mir_url), headers=headers).replace('\n', '')

                for media_label, media_url in re.compile(patron_media).findall(data):
                    urls.append(url_decode(media_url))

        itemlist = servertools.find_video_items(data='\n'.join(urls))
        for videoitem in itemlist:
            videoitem.title = item.title + videoitem.title
            videoitem.fulltitle = item.fulltitle
            videoitem.thumbnail = item.thumbnail
            videoitem.show = item.show
            videoitem.plot = item.plot
            videoitem.channel = __channel__

        return itemlist


def url_decode(url_enc):
    lenght = len(url_enc)
    if lenght % 2 == 0:
        len2 = lenght / 2
        first = url_enc[0:len2]
        last = url_enc[len2:lenght]
        url_enc = last + first
        reverse = url_enc[::-1]
        return base64.b64decode(reverse)

    last_car = url_enc[lenght - 1]
    url_enc[lenght - 1] = ' '
    url_enc = url_enc.strip()
    len1 = len(url_enc)
    len2 = len1 / 2
    first = url_enc[0:len2]
    last = url_enc[len2:len1]
    url_enc = last + first
    reverse = url_enc[::-1]
    reverse = reverse + last_car
    return base64.b64decode(reverse)
