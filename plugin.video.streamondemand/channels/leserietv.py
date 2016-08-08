# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para itafilmtv
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
#  By Costaplus
# ------------------------------------------------------------
import re
import sys
import urlparse
import urllib2
from core import config
from core import logger
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "leserietv"
__category__ = "F"
__type__ = "generic"
__title__ = "leserie.tv"
__language__ = "IT"

DEBUG = config.get_setting("debug")

host = "http://www.leserie.tv"

header = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', 'http://www.leserie.tv/streaming/']
]

def isGeneric():
    return True

#-----------------------------------------------------------------
def mainlist(item):
    logger.info("[leserietv.py] mainlist")
    itemlist =[]
    itemlist.append(Item(channel=__channel__,
                         action="novita",
                         title="[COLOR yellow]Novità[/COLOR]",
                         url="http://www.leserie.tv/streaming/",
                         thumbnail="http://www.ilmioprofessionista.it/wp-content/uploads/2015/04/TVSeries3.png",
                         fanart="http://www.macroidee.it/wp-content/uploads/2015/06/migliori-serie-da-vedere.jpg"))
    itemlist.append(Item(channel=__channel__,
                         action="lista_serie",
                         title="[COLOR azure]Tutte le serie[/COLOR]",
                         url="http://www.leserie.tv/streaming/",
                         thumbnail="http://www.ilmioprofessionista.it/wp-content/uploads/2015/04/TVSeries3.png",
                         fanart="http://www.macroidee.it/wp-content/uploads/2015/06/migliori-serie-da-vedere.jpg"))

    itemlist.append(Item(channel=__channel__,
                         title="[COLOR azure]Categorie[/COLOR]",
                         action="categorias",
                         url=host,
                         thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/All%20Movies%20by%20Genre.png"))

    itemlist.append(Item(channel=__channel__,
                         action="top50",
                         title="[COLOR azure]Top 50[/COLOR]",
                         url="http://www.leserie.tv/top50.html",
                         thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png",
                         fanart = "http://www.macroidee.it/wp-content/uploads/2015/06/migliori-serie-da-vedere.jpg"))

    itemlist.append(Item(channel=__channel__,
                         action="search",
                         title="[COLOR orange]Cerca...[/COLOR][I](minimo 3 caratteri)[/I]",
                         url="http://www.leserie.tv/index.php?do=search",
                         thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search",
                         fanart="http://www.kaushik.net/avinash/wp-content/uploads/2010/02/search_engine.png"))

    return itemlist
#=================================================================


#-----------------------------------------------------------------
def novita(item):
    logger.info("streamondemand.laserietv novità")
    itemlist = []

    data = scrapertools.cache_page(item.url)


    patron ='<div class="video-item-cover"[^<]+<a href="(.*?)">[^<]+<img src="(.*?)" alt="(.*?)">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        if (DEBUG): logger.info("title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")


        try:
            tmdbtitle = scrapedtitle
            plot, fanart, poster, extrameta = info(tmdbtitle)

            itemlist.append(Item(channel=__channel__,
                                 thumbnail=poster,
                                 fanart=fanart if fanart != "" else poster,
                                 extrameta=extrameta,
                                 plot=str(plot),
                                 action="episodi",
                                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                                 url=scrapedurl,
                                 fulltitle=scrapedtitle,
                                 show=scrapedtitle,
                                 folder=True))
        except:

             itemlist.append(Item(channel=__channel__,
                                  action="episodi",
                                  title=scrapedtitle,
                                  url=scrapedurl,
                                  thumbnail="",
                                  fulltitle=scrapedtitle,
                                  show=scrapedtitle))

    # Paginazione
    #===========================================================
    patron = '<div class="pages">(.*?)</div>'
    paginazione = scrapertools.find_single_match(data, patron)
    patron = '<span>.*?</span>.*?href="([^"]+)".*?</a>'
    matches = re.compile(patron, re.DOTALL).findall(paginazione)
    scrapertools.printMatches(matches)
    #===========================================================

    if len(matches) > 0:
        paginaurl = matches[0]
        itemlist.append(Item(channel=__channel__, action="novita", title="[COLOR orange]Successivo>>[/COLOR]", url=paginaurl,thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",folder=True))
        itemlist.append(Item(channel=__channel__, action="HomePage", title="[COLOR yellow]Torna Home[/COLOR]", folder=True))
    return itemlist
#=================================================================

#-----------------------------------------------------------------
def lista_serie(item):
    logger.info("[leserie.py] lista_serie")
    itemlist = []

    post="dlenewssortby=title&dledirection=asc&set_new_sort=dle_sort_cat&set_direction_sort=dle_direction_cat"

    data =scrapertools.cachePagePost(item.url,post=post)

    patron = '<div class="video-item-cover"[^<]+<a href="(.*?)">[^<]+<img src="(.*?)" alt="(.*?)">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        logger.info(scrapedurl + " " + scrapedtitle + scrapedthumbnail)

        try:
            tmdbtitle = scrapedtitle
            plot, fanart, poster, extrameta = info(tmdbtitle)

            itemlist.append(Item(channel=__channel__,
                                 thumbnail=poster,
                                 fanart=fanart if fanart != "" else poster,
                                 extrameta=extrameta,
                                 plot=str(plot),
                                 action="episodi",
                                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                                 url=scrapedurl,
                                 fulltitle=scrapedtitle,
                                 show=scrapedtitle,
                                 folder=True))
        except:

                itemlist.append(Item(channel=__channel__,
                             action="episodi",
                             title=scrapedtitle,
                             url=scrapedurl,
                             thumbnail=host + scrapedthumbnail,
                             fulltitle=scrapedtitle,
                             show=scrapedtitle))


    # Paginazione
    #===========================================================
    patron = '<div class="pages">(.*?)</div>'
    paginazione = scrapertools.find_single_match(data, patron)
    patron = '<span>.*?</span>.*?href="([^"]+)".*?</a>'
    matches = re.compile(patron, re.DOTALL).findall(paginazione)
    scrapertools.printMatches(matches)
    #===========================================================

    if len(matches) > 0:
        paginaurl = matches[0]
        itemlist.append(Item(channel=__channel__, action="lista_serie", title="[COLOR orange]Successivo>>[/COLOR]", url=paginaurl,thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",folder=True))
        itemlist.append(Item(channel=__channel__, action="HomePage", title="[COLOR yellow]Torna Home[/COLOR]", folder=True))
    return itemlist
#=================================================================

#-----------------------------------------------------------------
def categorias(item):
    logger.info("streamondemand.laserietv categorias")
    itemlist = []

    data = scrapertools.cache_page(item.url)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, '<ul class="dropdown-menu cat-menu">(.*?)</ul>')

    # The categories are the options for the combo
    patron = '<li ><a href="([^"]+)">(.*?)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = urlparse.urljoin(item.url, scrapedurl)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info(
                "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
                Item(channel=__channel__,
                     action="lista_serie",
                     title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                     url=scrapedurl,
                     thumbnail=scrapedthumbnail,
                     plot=scrapedplot))

    return itemlist


#=================================================================

#-----------------------------------------------------------------
def search(item,texto):
    logger.info("[laserietv.py] " + item.url + " search " + texto)
    itemlist =[]

    post = "do=search&subaction=search&search_start=0&full_search=0&result_from=1&story="+texto
    logger.debug(post)
    data = scrapertools.cachePagePost(item.url, post=post)

    patron = '<div class="video-item-cover"[^<]+<a href="(.*?)">[^<]+<img src="(.*?)" alt="(.*?)">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        logger.info(scrapedurl + " " + scrapedtitle + scrapedthumbnail)

        try:
            tmdbtitle = scrapedtitle
            plot, fanart, poster, extrameta = info(tmdbtitle)

            itemlist.append(Item(channel=__channel__,
                                 thumbnail=poster,
                                 fanart=fanart if fanart != "" else poster,
                                 extrameta=extrameta,
                                 plot=str(plot),
                                 action="episodi",
                                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                                 url=scrapedurl,
                                 fulltitle=scrapedtitle,
                                 show=scrapedtitle,
                                 folder=True))
        except:

                itemlist.append(Item(channel=__channel__,
                             action="episodi",
                             title=scrapedtitle,
                             url=scrapedurl,
                             thumbnail=host + scrapedthumbnail,
                             fulltitle=scrapedtitle,
                             show=scrapedtitle))

    return itemlist
#=================================================================

#-----------------------------------------------------------------
def top50(item):
    logger.info("[laserietv.py] top50")
    itemlist = []

    data = scrapertools.cache_page(item.url)

    patron = 'class="top50item">\s*<[^>]+>\s*<.*?="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        logger.debug(scrapedurl + " " + scrapedtitle)

        try:
            tmdbtitle = scrapedtitle
            plot, fanart, poster, extrameta = info(tmdbtitle)

            itemlist.append(Item(channel=__channel__,
                                 thumbnail=poster,
                                 fanart=fanart if fanart != "" else poster,
                                 extrameta=extrameta,
                                 plot=str(plot),
                                 action="episodi",
                                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                                 url=scrapedurl,
                                 fulltitle=scrapedtitle,
                                 show=scrapedtitle,
                                 folder=True))
        except:

            itemlist.append(Item(channel=__channel__,
                                 action="episodi",
                                 title=scrapedtitle,
                                 url=scrapedurl,
                                 thumbnail="",
                                 fulltitle=scrapedtitle,
                                 show=scrapedtitle))

    return itemlist
#=================================================================

#-----------------------------------------------------------------
def episodi(item):
    logger.info("[leserietv.py] episodi")
    itemlist = []

    data = scrapertools.cache_page(item.url)

    patron ='="megadrive-(.*?)".*?data-link="([^"]+)">Megadrive'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedtitle,scrapedurl in matches:
        scrapedtitle = scrapedtitle.replace('_',"x")

        itemlist.append(Item(channel=__channel__,
                             action="findvideos",
                             title=scrapedtitle,
                             url=scrapedurl,
                             thumbnail=item.thumbnail,
                             fanart=item.fanart if item.fanart != "" else item.scrapedthumbnail,
                             fulltitle=item.fulltitle,
                             show=item.fulltitle))


    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title="Aggiungi a preferiti",
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodi",
                 show=item.show))
        itemlist.append(
            Item(channel=item.channel,
                 title="Scarica tutti gli episodi della serie",
                 url=item.url,
                 action="download_all_episodes",
                 extra="episodi",
                 show=item.show))


    return itemlist
#=================================================================


#-----------------------------------------------------------------
def info(title):
    logger.info("[leserietv.py] info")
    try:
        from core.tmdb import Tmdb
        oTmdb= Tmdb(texto_buscado=title, tipo= "tv", include_adult="false", idioma_busqueda="it")
        count = 0
        if oTmdb.total_results > 0:
           extrameta = {}
           extrameta["Year"] = oTmdb.result["release_date"][:4]
           extrameta["Genre"] = ", ".join(oTmdb.result["genres"])
           extrameta["Rating"] = float(oTmdb.result["vote_average"])
           fanart=oTmdb.get_backdrop()
           poster=oTmdb.get_poster()
           plot=oTmdb.get_sinopsis()
           return plot, fanart, poster, extrameta
    except:
        pass
#=================================================================


#-----------------------------------------------------------------
def HomePage(item):
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")
#=================================================================
