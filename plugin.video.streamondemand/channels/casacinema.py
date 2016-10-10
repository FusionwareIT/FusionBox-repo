# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para casacinema
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
# ------------------------------------------------------------
import re
import urlparse

from core import config
from core import logger
from core import scrapertools
from core.item import Item
from core.tmdb import infoSod
from core import servertools

__channel__ = "casacinema"
__category__ = "F,S,A"
__type__ = "generic"
__title__ = "casacinema"
__language__ = "IT"

host = 'http://www.casa-cinema.org'

headers = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', '%s/genere/serie-tv' % host],
]


def isGeneric():
    return True


def mainlist(item):
    logger.info("streamondemand.casacinema mainlist")

    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film - Novita'[/COLOR]",
                     action="peliculas",
                     extra="film",
                     url="%s/genere/film" % host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film - HD[/COLOR]",
                     action="peliculas",
                     extra="film",
                     url="%s/?s=[HD]" % host,
                     thumbnail="http://jcrent.com/apple%20tv%20final/HD.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Categorie[/COLOR]",
                     action="categorias",
                     extra="film",
                     url="%s/genere/film" % host,
                     thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/All%20Movies%20by%20Genre.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film Sub - Ita[/COLOR]",
                     action="peliculas",
                     extra="film",
                     url="%s/genere/sub-ita" % host,
                     thumbnail="http://i.imgur.com/qUENzxl.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     extra="film",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[/COLOR]",
                     extra="serie",
                     action="peliculas_tv",
                     url="%s/genere/serie-tv" % host,
                     thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/New%20TV%20Shows.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Serie TV...[/COLOR]",
                     action="search",
                     extra="serie",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist


def search(item, texto):
    logger.info("[casacinema.py] " + item.url + " search " + texto)

    item.url = host + "?s=" + texto

    try:
        if item.extra == "serie":
            return peliculas_tv(item)
        else:
            return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def peliculas(item):
    logger.info("streamondemand.casacinema peliculas")

    itemlist = []

    # Descarga la pagina
    data = scrapertools.anti_cloudflare(item.url, headers)

    # Extrae las entradas (carpetas)
    patron = '<li><a href="([^"]+)" data-thumbnail="([^"]+)"><div><div class="title">(.*?)<'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        title = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedplot = ""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios" if item.extra == "serie" else "findvideos",
                 title=title,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=title,
                 show=title,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True), tipo='movie'))

    ## Paginación
    next_page = scrapertools.find_single_match(data, '<li class="active"><a href=[^>]+>[^>]+>[^>]+>[^>]+><a href="([^"]+)">')

    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title="[COLOR yellow]Torna Home[/COLOR]",
                 folder=True)),
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=next_page,
                 extra=item.extra,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png"))

    return itemlist


def peliculas_tv(item):
    logger.info("streamondemand.casacinema peliculas")

    itemlist = []

    # Descarga la pagina
    data = scrapertools.anti_cloudflare(item.url, headers)

    # Extrae las entradas (carpetas)
    patron = '<li><a href="([^"]+)" data-thumbnail="([^"]+)"><div><div class="title">(.*?)<'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        title = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedplot = ""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios" if item.extra == "serie" else "findvideos",
                 title=title,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=title,
                 show=title,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True), tipo='tv'))

    ## Paginación
    next_page = scrapertools.find_single_match(data, '<li class="active"><a href=[^>]+>[^>]+>[^>]+>[^>]+><a href="([^"]+)">')

    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title="[COLOR yellow]Torna Home[/COLOR]",
                 folder=True)),
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_tv",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=next_page,
                 extra=item.extra,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png"))

    return itemlist


def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")


def categorias(item):
    logger.info("streamondemand.casacinema categorias")

    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, 'Categorie(.*?)</ul>')

    # The categories are the options for the combo
    patron = '<a href="(.*?)">(.*?)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 extra=item.extra,
                 url=urlparse.urljoin(host, scrapedurl)))

    return itemlist


def episodios(item):
    logger.info("streamondemand.casacinema episodios")

    itemlist = []

    # Downloads page
    data = scrapertools.anti_cloudflare(item.url, headers)
    # Extracts the entries
    patron = '(.*?)<a href="(.*?)" target="_blank" rel="nofollow".*?>(.*?)</a>'
    matches = re.compile(patron).findall(data)

    for scrapedtitle, scrapedurl, scrapedserver in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        if scrapedtitle.startswith("<p>"):
            scrapedtitle = scrapedtitle[3:]

        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 title="[COLOR red]" + scrapedtitle + " [/COLOR]" + "[COLOR azure]" + item.fulltitle + " [/COLOR]" + "[COLOR orange] [" + scrapedserver + "][/COLOR]",
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 fulltitle=item.show + ' | ' + scrapedtitle,
                 extra=item.extra,
                 show=item.show))

    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title=item.title,
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodios" + "###" + item.extra,
                 show=item.show))
        itemlist.append(
            Item(channel=item.channel,
                 title="Scarica tutti gli episodi della serie",
                 url=item.url,
                 action="download_all_episodes",
                 extra="episodios" + "###" + item.extra,
                 show=item.show))

    return itemlist


def findvideos(item):
    logger.info("streamondemand.casacinema findvideos")

    data = item.url if item.extra == 'serie' else scrapertools.cache_page(item.url, headers=headers)

    itemlist = servertools.find_video_items(data=data)
    for videoitem in itemlist:
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist
