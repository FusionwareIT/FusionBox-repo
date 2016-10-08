# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# By Costaplus
# ------------------------------------------------------------
import re

import xbmc

from core import config
from core import logger
from core import scrapertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "filmissimi"
__category__ = "F"
__type__ = "generic"
__title__ = "filmissimi.net"
__language__ = "IT"

DEBUG = config.get_setting("debug")

host = "http://www.filmissimi.net"


def isGeneric():
    return True


# -------------------------------------------------------------------------------------------------------------------------------------------
def mainlist(item):
    log("mainlist", "init")
    itemlist = []

    itemlist.append(Item(channel=__channel__, action="elenco", title="[COLOR yellow]Novita'[/COLOR]"       , url=host                     , thumbnail=NovitaThumbnail, fanart=FilmFanart))
    itemlist.append(Item(channel=__channel__, action="elenco", title="[COLOR azure]Film al Cinema[/COLOR]" , url=host+"/genere/cinema"    , thumbnail=NovitaThumbnail, fanart=FilmFanart))
    itemlist.append(Item(channel=__channel__, action="elenco", title="[COLOR azure]Film Sub-Ita[/COLOR]"   , url=host+"/genere/sub-ita"   , thumbnail=NovitaThumbnail, fanart=FilmFanart))
    itemlist.append(Item(channel=__channel__, action="elenco", title="[COLOR azure]Film HD[/COLOR]"        , url=host+"/genere/film-in-hd", thumbnail=NovitaThumbnail, fanart=FilmFanart))
    itemlist.append(Item(channel=__channel__, action="genere", title="[COLOR azure]Genere[/COLOR]"         , url=host                     , thumbnail=GenereThumbnail, fanart=FilmFanart))
    itemlist.append(Item(channel=__channel__, action="search", title="[COLOR orange]Cerca..[/COLOR]"       ,                                thumbnail=CercaThumbnail , fanart=FilmFanart))

    return itemlist


# ===========================================================================================================================================

# -------------------------------------------------------------------------------------------------------------------------------------------
def genere(item):
    log("genere", "init")
    itemlist = []

    patron = '<a href="(.*?)">(.*?)</a>'
    for scrapedurl, scrapedtitle in scrapedSingle(item.url, '<h3 class="title">Categorie</h3><ul>(.*?)</ul>', patron):
        log("genere", "title=[" + scrapedtitle + "] url=[" + scrapedurl + "]")
        itemlist.append(Item(channel=__channel__, action="elenco", title="[COLOR azure]"+ scrapedtitle+"[/COLOR]", url=scrapedurl, thumbnail=NovitaThumbnail, fanart=FilmFanart))

    return itemlist


# ===========================================================================================================================================

# -------------------------------------------------------------------------------------------------------------------------------------------
def elenco(item):
    log("elenco", "init")
    itemlist = []

    patron = '<img src="(.*?)"[^=]+=.*?[^=]+="Thumbnail[^>]+>[^>]+><h2><a.*?href="(.*?)"[^>]+>(.*?)</a></h2>'
    for scrapedthumbnail, scrapedurl, scrapedtitle in scrapedSingle(item.url, '<ul class="recent-posts">(.*?)</ul>', patron):
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        log("elenco", "title=[" + scrapedtitle + "] url=[" + scrapedurl + "] thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail), tipo="movie"))

    # Paginazione
    # ===========================================================================================================================
    matches = scrapedSingle(item.url, '<div class="navigation">(.*?)</div>',
                            "current'>.*?</span>.*?class='page-numbers'.*?href='(.*?)'>.*?</a>")
    if len(matches) > 0:
        paginaurl = matches[0]
        itemlist.append(Item(channel=__channel__, action="elenco", title=AvantiTxt, url=paginaurl, thumbnail=AvantiImg))
        itemlist.append(Item(channel=__channel__, action="HomePage", title=HomeTxt, folder=True))
    else:
        itemlist.append(Item(channel=__channel__, action="mainlist", title=ListTxt, folder=True))
    # ===========================================================================================================================
    return itemlist


# ===========================================================================================================================================

# -------------------------------------------------------------------------------------------------------------------------------------------
def search(item, texto):
    log("search", "init texto=[" + texto + "]")
    itemlist = []
    url = "http://www.filmissimi.net/?s=" + texto

    patron = '<img src="(.*?)"[^=]+=.*?[^=]+="Thumbnail[^>]+>[^>]+><h2><a.*?href="(.*?)"[^>]+>(.*?)</a></h2>'
    for scrapedthumbnail, scrapedurl, scrapedtitle in scrapedSingle(url, '<ul class="recent-posts">(.*?)</ul>', patron):
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        log("elenco", "title=[" + scrapedtitle + "] url=[" + scrapedurl + "] thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail), tipo="movie"))

    # Paginazione
    # ===========================================================================================================================
    matches = scrapedSingle(url, '<div class="navigation">(.*?)</div>', "current'>.*?</span>.*?class='page-numbers'.*?href='(.*?)'>.*?</a>")

    if len(matches) > 0:
        paginaurl = matches[0]
        itemlist.append(Item(channel=__channel__, action="elenco", title=AvantiTxt, url=paginaurl, thumbnail=AvantiImg))
        itemlist.append(Item(channel=__channel__, action="HomePage", title=HomeTxt, folder=True))
    else:
        itemlist.append(Item(channel=__channel__, action="mainlist", title=ListTxt, folder=True))
    # ===========================================================================================================================
    return itemlist


# ===========================================================================================================================================

# =================================================================
# Funzioni di servizio
# -----------------------------------------------------------------
def scrapedAll(url="", patron=""):
    matches = []
    data = scrapertools.cache_page(url)
    log("data ->" + data)
    MyPatron = patron
    matches = re.compile(MyPatron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    return matches


# =================================================================

# -----------------------------------------------------------------
def scrapedSingle(url="", single="", patron=""):
    matches = []
    data = scrapertools.cache_page(url)
    elemento = scrapertools.find_single_match(data, single)
    log("elemento ->" + data)
    matches = re.compile(patron, re.DOTALL).findall(elemento)
    scrapertools.printMatches(matches)

    return matches


# =================================================================

# -----------------------------------------------------------------
def log(funzione="", stringa="", canale=__channel__):
    logger.info("[" + canale + "].[" + funzione + "] " + stringa)


# =================================================================

# -----------------------------------------------------------------
def HomePage(item):
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")


# =================================================================

# =================================================================
# riferimenti di servizio
# ---------------------------------------------------------------------------------------------------------------------------------
NovitaThumbnail = "https://superrepo.org/static/images/icons/original/xplugin.video.moviereleases.png.pagespeed.ic.j4bhi0Vp3d.png"
GenereThumbnail = "https://farm8.staticflickr.com/7562/15516589868_13689936d0_o.png"
FilmFanart = "https://superrepo.org/static/images/fanart/original/script.artwork.downloader.jpg"
CercaThumbnail = "http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"
CercaFanart = "https://i.ytimg.com/vi/IAlbvyBdYdY/maxresdefault.jpg"
HomeTxt = "[COLOR yellow]Torna Home[/COLOR]"
ListTxt = "[COLOR orange]Torna a elenco principale [/COLOR]"
AvantiTxt = "[COLOR orange]Successivo>>[/COLOR]"
AvantiImg = "http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png"
thumbnail = "http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"
# ----------------------------------------------------------------------------------------------------------------------------------#----------------------------------------------------------------------------------------------------------------------------------
