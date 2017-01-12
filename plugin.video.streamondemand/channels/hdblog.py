# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para hdblog
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#------------------------------------------------------------
import re
import urlparse

from core import config
from core import logger
from core import scrapertools
from core.item import Item

__channel__ = "hdblog"
__category__ = "D"
__type__ = "generic"
__title__ = "hdblog (IT)"
__language__ = "IT"


DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("streamondemand.hdblog mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Video recensioni tecnologiche[/COLOR]",
                     action="peliculas",
                     url="http://www.hdblog.it/video/",
                     thumbnail="http://www.crat-arct.org/uploads/images/tic%201.jpg"),
                Item(channel=__channel__,
                     title="[COLOR azure]Categorie[/COLOR]",
                     action="categorias",
                     url="http://www.hdblog.it/video/",
                     thumbnail="http://www.crat-arct.org/uploads/images/tic%201.jpg")]

    return itemlist

def categorias(item):
    logger.info("streamondemand.hdblog categorias")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Narrow search by selecting only the combo
    start = data.find('<section class="left_toolbar" style="float: left;width: 125px;margin-right: 18px;">')
    end = data.find('</section>', start)
    bloque = data[start:end]

    # The categories are the options for the combo  
    patron = '<a href="([^"]+)"[^>]+><span>(.*?)</span>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        #scrapedtitle = scrapertools.decodeHtmlentities(titulo)
        #scrapedurl = urlparse.urljoin(item.url, url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl + "video/",
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot))

    return itemlist

def peliculas(item):
    logger.info("streamondemand.hdblog peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron  = '<a class="thumb_new_image" href="([^"]+)">\s*<img[^s]+src="([^"]+)"[^>]+>\s*</a>\s*[^>]+>\s*(.*?)\s*<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", fulltitle=scrapedtitle, show=scrapedtitle, title=scrapedtitle, url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    # Extrae el paginador
    patronvideos  = '<span class="attiva">[^>]+>[^=]+="next" href="(.*?)" class="inattiva">'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        itemlist.append( Item(channel=__channel__, action="HomePage", title="[COLOR yellow]Torna Home[/COLOR]" , folder=True) )
        itemlist.append( Item(channel=__channel__, action="peliculas", title="[COLOR orange]Avanti >>[/COLOR]" , url=scrapedurl , folder=True) )

    return itemlist

def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")

