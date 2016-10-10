# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canale per toointalia
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------
import re

from core import config
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "toonitalia"
__category__ = "A"
__type__ = "generic"
__title__ = "Toonitalia"
__language__ = "IT"

host = "http://toonitalia.altervista.org"

headers = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0'],
    ['Accept-Encoding', 'gzip, deflate']
]

DEBUG = config.get_setting("debug")


def isGeneric():
    return True


def mainlist(item):
    logger.info("streamondemand.toointalia mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Home[/COLOR]",
                     action="anime",
                     url=host,
                     thumbnail="http://i.imgur.com/a8Vwz1V.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Anime[/COLOR]",
                     action="anime",
                     url=host + "/category/anime/",
                     thumbnail="http://i.imgur.com/a8Vwz1V.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Anime Sub-Ita[/COLOR]",
                     action="anime",
                     url=host + "/category/anime-sub-ita/",
                     thumbnail="http://i.imgur.com/a8Vwz1V.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film Animazione[/COLOR]",
                     action="animazione",
                     url="%s/category/film-animazione/" % host,
                     thumbnail="http://i.imgur.com/a8Vwz1V.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[/COLOR]",
                     action="anime",
                     url=host + "/category/serie-tv/",
                     thumbnail="http://i.imgur.com/a8Vwz1V.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     extra="anime",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist


def search(item, texto):
    logger.info("[toonitalia.py] " + item.url + " search " + texto)
    item.url = host + "/?s=" + texto
    try:
        return anime(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def anime(item):
    logger.info("streamondemand.toointalia peliculas")

    itemlist = []

    ## Descarga la pagina
    data = scrapertools.cache_page(item.url)

    ## Extrae las entradas (carpetas)
    patron = '<figure class="post-image left">\s*<a href="([^"]+)"><img src="[^"]*"[^l]+lt="([^"]+)" /></a>\s*</figure>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedthumbnail = ""

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodi",
                 title=title,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=title,
                 show=title,
                 viewmode="movie_with_plot"), tipo='tv'))

    # Older Entries
    patron = '<link rel="next" href="([^"]+)" />'
    next_page = scrapertools.find_single_match(data, patron)
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 title="[COLOR orange]Post più vecchi...[/COLOR]",
                 url=next_page,
                 action="anime",
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png"))

    return itemlist


def animazione(item):
    logger.info("streamondemand.toointalia peliculas")

    itemlist = []

    ## Descarga la pagina
    data = scrapertools.cache_page(item.url)

    ## Extrae las entradas (carpetas)
    patron = '<figure class="post-image left">\s*<a href="([^"]+)"><img src="[^"]*"[^l]+lt="([^"]+)" /></a>\s*</figure>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        title = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedthumbnail = ""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="film",
                 title=title,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=title,
                 show=title,
                 viewmode="movie_with_plot"), tipo='movie'))

    # Older Entries
    patron = '<link rel="next" href="([^"]+)" />'
    next_page = scrapertools.find_single_match(data, patron)
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 title="[COLOR orange]Post più vecchi...[/COLOR]",
                 url=next_page,
                 action="animazione",
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png"))

    return itemlist


def episodi(item):
    logger.info("toonitalia.py episodi")

    itemlist = []

    # Downloads page
    data = scrapertools.cache_page(item.url)
    # Extracts the entries
    patron = '<a\s*href="([^"]+)"\s*target="_blank">([^<]+)</a><'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        if 'adf.ly' not in scrapedurl:
            scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
            itemlist.append(
                Item(channel=__channel__,
                     action="findvid",
                     title=scrapedtitle,
                     thumbnail=item.thumbnail,
                     url=scrapedurl))

    return itemlist


def film(item):
    logger.info("toonitalia.py film")

    itemlist = []

    # Downloads page
    data = scrapertools.cache_page(item.url)
    # Extracts the entries
    #    patron = '<img class="aligncenter.*?src="([^"]+)" alt="([^"]+)".*?<strong><a href="([^"]+)" target="_blank">'
    patron = '<img.*?src="([^"]+)".*?alt="([^"]+)".*?strong><a href="([^"]+)" target="_blank">'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedthumbnail, scrapedtitle, scrapedurl in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)

        itemlist.append(
            Item(channel=__channel__,
                 action="findvid",
                 title=scrapedtitle,
                 thumbnail=scrapedthumbnail,
                 url=scrapedurl))
    # Older Entries
    patron = '<link rel="next" href="([^"]+)" />'
    next_page = scrapertools.find_single_match(data, patron)
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 title="[COLOR orange]Post più vecchi...[/COLOR]",
                 url=next_page,
                 action="film",
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png"))
    return itemlist


def findvid(item):
    logger.info("[toonitalia.py] findvideos")

    itemlist = servertools.find_video_items(data=item.url)
    for videoitem in itemlist:
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist
