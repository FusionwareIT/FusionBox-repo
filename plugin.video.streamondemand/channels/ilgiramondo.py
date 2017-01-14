# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para ilgiramondo
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#------------------------------------------------------------
import re
import urlparse

from core import config
from core import logger
from core import scrapertools
from core.item import Item

__channel__ = "ilgiramondo"
__category__ = "D"
__type__ = "generic"
__title__ = "ilgiramondo (IT)"
__language__ = "IT"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("streamondemand.ilgiramondo mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Video di Viaggi[/COLOR]", action="peliculas", url="http://www.ilgiramondo.net/video-vacanze-viaggi/", thumbnail="http://hotelsjaisalmer.com/wp-content/uploads/2016/10/Travel1.jpg"))
    
    return itemlist

def peliculas(item):
    logger.info("streamondemand.ilgiramondo peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron  = '<article id=[^>]+><div class="space">\s*<a href="([^"]+)"><img[^s]+src="(.*?)"[^>]+><\/a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedthumbnail in matches:
        html = scrapertools.cache_page(scrapedurl)
        start = html.find("</script></div>")
        end = html.find("</p>", start)
        scrapedplot = html[start:end]
        scrapedplot = re.sub(r'<[^>]*>', '', scrapedplot)
        scrapedplot = scrapertools.decodeHtmlentities(scrapedplot)
        html = scrapertools.cache_page(scrapedurl)
        start = html.find("<title>")
        end = html.find("</title>", start)
        scrapedtitle = html[start:end]
        scrapedtitle = re.sub(r'<[^>]*>', '', scrapedtitle)
        scrapedtitle = scrapedtitle.replace(" | Video Di Viaggi E Vacanze", "")
        #scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", fulltitle=scrapedtitle, show=scrapedtitle, title=scrapedtitle, url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    # Extrae el paginador
    patronvideos  = '<a class="next page-numbers" href="(.*?)">Successivo'
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

