# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para documentaristreaming
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# by dentaku65, DrZ3r0
# ------------------------------------------------------------
import re
import urlparse

from core import config
from core import logger
from core import scrapertools
from core.item import Item

__channel__ = "documentaristreaming"
__category__ = "F,D"
__type__ = "generic"
__title__ = "documentaristreaming (TV)"
__language__ = "IT"

sito = "https://www.documentaristreaming.net/"

headers = [
    ['User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0'],
    ['Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'],
    ['Accept-Encoding', 'gzip, deflate, br'],
    ['Accept-Language', 'en-US,en;q=0.5'],
    ['Connection', 'keep-alive'],
    ['DNT', '1'],
    ['Upgrade-Insecure-Requests', '1'],
    ['Cache-Control', 'max-age=0']
]

DEBUG = config.get_setting("debug")


def isGeneric():
    return True


def mainlist(item):
    logger.info("streamondemand.documentaristreaming mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Aggiornamenti[/COLOR]",
                     action="peliculas",
                     url="https://www.documentaristreaming.net/page/1/",
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Categorie[/COLOR]",
                     action="categorias",
                     url=sito,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist


def peliculas(item):
    logger.info("streamondemand.documentaristreaming peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url, headers=headers)
    bloque = scrapertools.get_match(data, '<h2 class="vwspc-section-title">(.*?)<nav class="vw-page-navigation clearfix">')


    # Extrae las entradas (carpetas)
    patron = '<a class="vw-post-box-thumbnail" href="([^"]+)"[^>]+>\s*<img[^s]+src="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedthumbnail in matches:
        scrapedtitle = scrapedurl
        scrapedtitle = scrapedtitle.replace("https://www.documentaristreaming.net/","")
        scrapedtitle = scrapedtitle.replace("-"," ")
        scrapedtitle = scrapedtitle.replace("/","")
        scrapedtitle = scrapedtitle.lower()
        scrapedtitle = scrapedtitle.title()
        scrapedplot = ""
        if (DEBUG): logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))

    # Extrae el paginador
    patronvideos = '<a class="next page-numbers" href="(.*?)">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title="[COLOR yellow]Torna Home[/COLOR]",
                 folder=True)),
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))

    return itemlist

def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")

def categorias(item):
    logger.info("streamondemand.documentaristreaming categorias")
    itemlist = []

    data = scrapertools.cache_page(item.url, headers=headers)
    logger.info(data)

    # Narrow search by selecting only the combo
    start = data.find('<ul class="sub-menu menu-odd  menu-depth-1">')
    end = data.find('</ul>', start)
    bloque = data[start:end]

    # The categories are the options for the combo  
    patron = '<li[^>]+><a[^h]+href="(.*?)"[^>]+><span>(.*?)<[^>]+><[^>]+><[^>]+>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for url, titulo in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(titulo)
        scrapedurl = urlparse.urljoin(item.url, url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot))

    return itemlist

def search(item,texto):
    logger.info("[documentaristreaming.py] "+item.url+" search "+texto)
    item.url = "http://documentaristreaming.net/?s="+texto
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []
