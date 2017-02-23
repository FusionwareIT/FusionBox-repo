# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para ilgeniodellostreaming
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

__channel__ = "ilgeniodellostreaming"
__category__ = "F,S,A"
__type__ = "generic"
__title__ = "ilgeniodellostreaming (IT)"
__language__ = "IT"

DEBUG = config.get_setting("debug")

host = "http://ilgeniodellostreaming.cc"

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
    logger.info("streamondemand.ilgeniodellostreaming mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Ultimi Film Inseriti[/COLOR]",
                     action="peliculas",
                     url="%s/film/" % host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film Per Categoria[/COLOR]",
                     action="categorias",
                     url=host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[/COLOR]",
                     action="serie",
                     url="%s/serie/" % host,
                     thumbnail="http://www.ilmioprofessionista.it/wp-content/uploads/2015/04/TVSeries3.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Anime[/COLOR]",
                     action="serie",
                     url="%s/anime/" % host,
                     thumbnail="http://orig09.deviantart.net/df5a/f/2014/169/2/a/fist_of_the_north_star_folder_icon_by_minacsky_saya-d7mq8c8.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist


def categorias(item):
    logger.info("streamondemand.ilgeniodellostreaming categorias")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url, headers=headers)
    bloque = scrapertools.get_match(data, '<ul class="genres scrolling">(.*?)</ul>')

    # Extrae las entradas (carpetas)
    patron = '<li[^>]+><a href="(.*?)"[^>]+>(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        logger.info("title=[" + scrapedtitle + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png",
                 folder=True))

    return itemlist

def search(item, texto):
    logger.info("[ilgeniodellostreaming.py] " + item.url + " search " + texto)
    item.url = "http://ilgeniodellostreaming.cc/?s=" + texto

    try:
        return peliculas_src(item)

    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)

    return []

def peliculas_src(item):
    logger.info("streamondemand.ilgeniodellostreaming peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url, headers=headers)

    patron = '<div class="thumbnail animation-2"><a href="(.*?)"><img src="(.*?)" alt="(.*?)" />[^>]+>(.*?)</span>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedtipo in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        logger.info("title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")

        if scrapedtipo=="TV":
            itemlist.append(infoSod(
                Item(channel=__channel__,
                     action="episodios",
                     fulltitle=scrapedtitle,
                     show=scrapedtitle,
                     title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                     url=scrapedurl,
                     thumbnail=scrapedthumbnail,
                     folder=True), tipo='tv'))
        else:
            itemlist.append(infoSod(
                Item(channel=__channel__,
                     action="findvideos",
                     fulltitle=scrapedtitle,
                     show=scrapedtitle,
                     title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                     url=scrapedurl,
                     thumbnail=scrapedthumbnail,
                     folder=True), tipo='movie'))

    return itemlist

def peliculas(item):
    logger.info("streamondemand.ilgeniodellostreaming peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url, headers=headers)

    # Extrae las entradas (carpetas)
    patron = '<div class="poster">\s*<a href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"></a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedplot = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
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
    patronvideos = '<span class="current">[^<]+<[^>]+><a href=\'(.*?)\''
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

def serie(item):
    logger.info("streamondemand.ilgeniodellostreaming peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url, headers=headers)

    # Extrae las entradas (carpetas)
    patron = '<div class="poster">\s*<a href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"></a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedplot = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        if DEBUG: logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))

    # Extrae el paginador
    patronvideos = '<span class="current">[^<]+<[^>]+><a href=\'(.*?)\''
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

def episodios(item):
    logger.info("streamondemand.ilgeniodellostreaming episodios")
    itemlist = []


    patron='<ul class="episodios">.*?</ul>'

    data = scrapertools.cache_page(item.url, headers=headers)
    matches = re.compile(patron, re.DOTALL).findall(data)

    for match in matches:

        patron='<li><div class="imagen"><a href="(.*?)">[^>]+>[^>]+>[^>]+><.*?numerando">(.*?)<[^>]+>[^>]+>[^>]+>(.*?)</a>'
        episodi = re.compile(patron, re.DOTALL).findall(match)

        for scrapedurl,scrapednumber,scrapedtitle in episodi:
            n0 = scrapednumber.replace(" ","")
            n1 = n0.replace("-","x")

            itemlist.append(Item(channel=__channel__,
                                 action="findvideos",
                                 fulltitle=n1 + " " + scrapedtitle,
                                 show=n1 + " " + scrapedtitle,
                                 title= n1 + " [COLOR orange] " + scrapedtitle + "[/COLOR]",
                                 url=scrapedurl,
                                 thumbnail=item.thumbnail,
                                 plot=item.plot,
                                 folder=True))

    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title=item.title + " [COLOR yellow] Aggiungi alla liberia [/COLOR]",
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodios",
                 show=item.show))
        itemlist.append(
            Item(channel=item.channel,
                 title="Scarica tutti gli episodi della serie",
                 url=item.url,
                 action="download_all_episodes",
                 extra="episodios",
                 show=item.show))

    return itemlist


def findvideos(item):
    logger.info("[streaminglove.py] play")

    data = scrapertools.cache_page(item.url, headers=headers)

    patron = '<td><a class="link_a" href="(.*?)" target="_blank">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for url in matches:
        html = scrapertools.cache_page(url, headers=headers)
        data += str(scrapertools.find_multiple_matches(html, 'window.location.href=\'(.*?)\''))

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
