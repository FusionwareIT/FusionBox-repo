# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para strfilm
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------
import re
import urlparse

from core import config
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "strfilm"
__category__ = "F"
__type__ = "generic"
__title__ = "filmitalia.tv (IT)"
__language__ = "IT"

DEBUG = config.get_setting("debug")

host = "http://www.strfilm.com/"

dec_fly = "http://www.i2w.biz/adf.ly/?url="

def isGeneric():
    return True


def mainlist(item):
    logger.info("streamondemand.strfilm mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Ultimi Film Inseriti[/COLOR]",
                     action="peliculas",
                     url=host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film Per Categoria[/COLOR]",
                     action="categorias",
                     url="http://www.strfilm.com/lista-film/",
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist


def categorias(item):
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    bloque = scrapertools.get_match(data, '<div class="cats-widget">(.*?)</ul>')

    # Extrae las entradas (carpetas)
    patron = '<a href="([^"]+)" >(.*?)</a>(.*?)\s*</li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle, scrapedtot in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        if DEBUG: logger.info("title=[" + scrapedtitle + "], url=[" + scrapedurl + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR][COLOR gray]" + scrapedtot + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/All%20Movies%20by%20Genre.png",
                 folder=True))

    return itemlist


def search(item, texto):
    logger.info("[strfilm.py] " + item.url + " search " + texto)
    item.url = host + "/?s=" + texto
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def peliculas(item):
    logger.info("streamondemand.strfilm peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron = '<div class="blog-item-wrap">\s*<a id="images" href="([^"]+)" title="(.*?)"[^>]+>\s*<img[^s]+src="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedplot = ""
        #scrapedthumbnail = ""
        # html = scrapertools.cache_page(scrapedurl)
        # start = html.find("<div class=\"description\">")
        # end = html.find("</p>", start)
        # scrapedplot = html[start:end]
        # scrapedplot = re.sub(r'<[^>]*>', '', scrapedplot)
        # scrapedplot = scrapertools.decodeHtmlentities(scrapedplot)
        scrapedthumbnail = urlparse.urljoin(item.url, match.group(3))
        scrapedtitle = scrapertools.unescape(match.group(2))
        scrapedurl = urlparse.urljoin(item.url, match.group(1))
        if DEBUG: logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))

    # Extrae el paginador
    patronvideos = '<a class="next page-numbers" href="(.*?)">Older'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

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

def findvideos(item):
    logger.info("[strfilm.py] findvideos")

    data = scrapertools.cache_page(item.url)

    patron = '<iframe id="ifrm" style="width:100%; height:400px;" src="([^"]+)"></iframe>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for url in matches:
        if 'adf.ly' in url:
            url = dec_fly + url
        html = scrapertools.cache_page(url)
        data += str(scrapertools.find_single_match(html, '<p>Your URL is <a href="(.*?)">'))

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist

def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")

#channel disabled
