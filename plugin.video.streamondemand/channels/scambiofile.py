# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para scambiofile
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "scambiofile"
__category__ = "F"
__type__ = "generic"
__title__ = "Scambiofile (IT)"
__language__ = "IT"

DEBUG = config.get_setting("debug")

site = "http://scambiofile.info"

def isGeneric():
    return True

def mainlist(item):
    logger.info("streamondemand.scambiofile mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Novità-Film .torrent stream[/COLOR]", action="peliculas", url="http://www.scambiofile.info/browse.php?cat=1", thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"))
    itemlist.append( Item(channel=__channel__, title="[COLOR yellow]Cerca...[/COLOR]", action="search", thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"))
    
    return itemlist

def search(item,texto):
    logger.info("[scambiofile.py] "+item.url+" search "+texto)
    item.url = "http://www.scambiofile.info/browse.php?cat=1&search="+texto
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def peliculas(item):
    logger.info("streamondemand.scambiofile peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url, timeout=10)

    # Extrae las entradas (carpetas)
    patron = '<a <td align="left">[^)]+.[^)]+.[^=]+=\'(.*?)\' target=\'_blank\'>(.*?)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        title = scrapedtitle.split("(")[0]
        url = scrapedurl
        url = url.replace("%2F", "/")
        url = url.replace("%3F", "?")
        url = url.replace("%26n%3", "&n=")
        url = url.replace("/details.php", "http://www.scambiofile.info/details.php")
        scrapedplot = ""
        scrapedthumbnail = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+url+"], thumbnail=["+scrapedthumbnail+"]")
        try:
           plot, fanart, poster, extrameta = info(title)

           itemlist.append( Item(channel=__channel__, action="play", fulltitle=scrapedtitle, show=scrapedtitle, title="[COLOR darkkhaki].torrent [/COLOR]""[COLOR azure]"+scrapedtitle+"[/COLOR]" , url=url , thumbnail=poster , plot=str(plot) , extrameta=extrameta , fanart=fanart if fanart != "" else poster, folder=True) )
        except:
           itemlist.append( Item(channel=__channel__, action="play", fulltitle=scrapedtitle, show=scrapedtitle, title="[COLOR darkkhaki].torrent [/COLOR]""[COLOR azure]"+scrapedtitle+"[/COLOR]" , url=url , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    # Extrae el paginador
    patronvideos  = '<td class="highlight"><b>[^h]+href="([^"]+)"[^>]+>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        url = urlparse.urljoin(item.url,matches[0])
        url = url.replace("&amp;", "&")
        itemlist.append( Item(channel=__channel__, action="peliculas", title="[COLOR orange]Successivo>>[/COLOR]" , url=url , thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png", folder=True) )

    return itemlist

def play(item):
    logger.info("[scambiofile.py] play")
    itemlist = []

    data = scrapertools.cache_page(item.url)

    patron = '<a class=\'btn btn-warning small\' href="(magnet[^&]+)[^>]+>'
    patron = urllib.unquote(patron).decode('utf8')
    link = scrapertools.find_single_match(data, patron)
    link = urlparse.urljoin(item.url,link)

    itemlist.append( Item(channel=__channel__, action=play, server="torrent", title=item.title , url=link , thumbnail=item.thumbnail , plot=item.plot , folder=False) )

    return itemlist

def info(title):
    logger.info("streamondemand.altadefinizioneone info")
    try:
        from core.tmdb import Tmdb
        oTmdb = Tmdb(texto_buscado=title, tipo="movie", include_adult="false", idioma_busqueda="it")
        if oTmdb.total_results > 0:
            extrameta = {"Year": oTmdb.result["release_date"][:4],
                         "Genre": ", ".join(oTmdb.result["genres"]),
                         "Rating": float(oTmdb.result["vote_average"])}
            fanart = oTmdb.get_backdrop()
            poster = oTmdb.get_poster()
            plot = oTmdb.get_sinopsis()
            return plot, fanart, poster, extrameta
    except:
        pass
