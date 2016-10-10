# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para corsaronero
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------
import re
import urlparse

from core import config
from core import logger
from core import scrapertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "corsaronero"
__category__ = "F"
__type__ = "generic"
__title__ = "Corsaro Nero (IT)"
__language__ = "IT"

DEBUG = config.get_setting("debug")

host = 'http://ilcorsaronero.info'

headers = [
    ['User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0'],
    ['Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', '%s/cat/1' % host]
]


def isGeneric():
    return True


def mainlist(item):
    logger.info("streamondemand.corsaronero mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Novità-Film .torrent stream[/COLOR]",
                     action="peliculas",
                     url="%s/cat/1" % host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     extra="torrent",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist


def search(item, texto):
    logger.info("[corsaronero.py] " + item.url + " search " + texto)
    item.url = host + "/argh.php?search=" + texto
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def peliculas(item):
    logger.info("streamondemand.corsaronero peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url, headers=headers)

    # Extrae las entradas (carpetas)
    patron = '<A class="tab" HREF="(/tor/[0-9]+/)[^>]+>(.*?)</A>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = scrapedtitle.replace(".", " ").replace("19", "(").replace("20", "(").split("(")[0]
        scrapedurl = urlparse.urljoin(host, scrapedurl)
        scrapedplot = ""
        scrapedthumbnail = ""
        if (DEBUG): logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")

        itemlist.append(infoSod(Item(channel=__channel__,
                                     action="play",
                                     title="[COLOR darkkhaki].torrent [/COLOR][COLOR azure]" + scrapedtitle + "[/COLOR]",
                                     fulltitle=scrapedtitle,
                                     url=scrapedurl,
                                     thumbnail=scrapedthumbnail),
                                tipo="movie"))
    # Extrae el paginador
    patronvideos = '<a href="([^>"]+)">pagine successive'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(host, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo>>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))

    return itemlist


def play(item):
    logger.info("[corsaronero.py] play")
    itemlist = []

    data = scrapertools.cache_page(item.url, headers=headers)

    patron = '<a class="forbtn magnet" target="_blank" href="(magnet[^"]+)" title="Magnet" ></a>'
    link = scrapertools.find_single_match(data, patron)

    itemlist.append(
        Item(channel=__channel__,
             action=play,
             server="torrent",
             title=item.title,
             url=link,
             thumbnail=item.thumbnail,
             plot=item.plot,
             folder=False))

    return itemlist
