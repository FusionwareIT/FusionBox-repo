# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para altadefinizione01
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------
import re

import xbmc

from core import config
from core import logger
from core import scrapertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "altadefinizioneclub"
__category__ = "F,S,A"
__type__ = "generic"
__title__ = "AltaDefinizioneclub"
__language__ = "IT"

host = "http://altadefinizione.club"


DEBUG = config.get_setting("debug")

def isGeneric():
    return True


def mainlist(item):
    logger.info("streamondemand.altadefinizione01 mainlist")
    itemlist = []
    itemlist.append(Item(channel=__channel__,title="[COLOR azure]Prime visioni[/COLOR]",action="peliculas",url="%s/prime_visioni/" % host,thumbnail=ThumbPrimavisione,fanart=fanart))
    itemlist.append(Item(channel=__channel__,title="[COLOR azure]Ultime novità[/COLOR]",action="peliculas",url="%s/news/" % host,thumbnail=ThumbPrimavisione,fanart=fanart))
    itemlist.append(Item(channel=__channel__,title="[COLOR azure]Film in HD[/COLOR]",action="peliculas", url="http://altadefinizione.club/?s=[HD]",thumbnail=ThumbPrimavisione, fanart=fanart))
    itemlist.append(Item(channel=__channel__,title="[COLOR azure]Genere[/COLOR]",action="genere",url=host+"/", thumbnail=ThumbPrimavisione, fanart=fanart))
    itemlist.append(Item(channel=__channel__,title="[COLOR yellow]Cerca...[/COLOR]",action="search", thumbnail=ThumbPrimavisione, fanart=fanart))


    return itemlist


def peliculas(item):
    logger.info("streamondemand.altadefinizioneclub peliculas")
    itemlist = []

    patron = 'class="box-single-mini-post">[^<]+<.*?href="(.*?)".*?title="(.*?)"[^<]+<[^<]+<[^<]+<.*?lazy".*?src="(.*?)"'
    for scrapedurl,scrapedtitle,scrapedthumbnail  in scrapedAll(item.url,patron):
        logger.info("title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        xbmc.log(("title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]"))
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = scrapedtitle.replace("[HD]","")
        itemlist.append(infoSod(
                        Item(channel=__channel__,
                              action="findvideos",
                               title=scrapedtitle,
                           fulltitle=scrapedtitle,
                                 url=scrapedurl,
                           thumbnail=scrapedthumbnail,
                            viewmode="movie"),
                                tipo="movie",))

    # Paginazione
    # ===========================================================================================================================
    matches = scrapedSingle(item.url, '<span class=\'pages\'>(.*?)class="clearfix"',"class='current'>.*?</span>.*?href=\"(.*?)\">.*?</a>")
    if len(matches) > 0:
        paginaurl = scrapertools.decodeHtmlentities(matches[0])
        itemlist.append(Item(channel=__channel__, action="peliculas", title=AvantiTxt, url=paginaurl, thumbnail=AvantiImg))
        itemlist.append(Item(channel=__channel__, action="HomePage", title=HomeTxt, thumbnail=ThumbnailHome, folder=True))
    else:
        itemlist.append(Item(channel=__channel__, action="mainlist", title=ListTxt, thumbnail=ThumbnailHome,folder=True))
    # ===========================================================================================================================
    return itemlist

def search(item, texto):
    logger.info("[altadefinizioneclub.py] " + item.url + " search " + texto)
    itemlist=[]
    item.url = "http://altadefinizione.club/?s=%s" % texto

    return peliculas(item)


def genere(item):
    itemlist=[]

    patron='<li class="cat-item.*?"[^<]+<.*?href="(.*?)".*?>(.*?)</a>'
    single='class="box-sidebar-header">[^C]+Categorie(.*?)class="box-sidebar general">'
    for scrapedurl,scrapedtitle in scrapedSingle(item.url,single,patron):

        itemlist.append(Item(channel=__channel__,
                              action="peliculas",
                               title=scrapedtitle,
                           fulltitle=scrapedtitle,
                                 url=scrapedurl,
                           thumbnail=""))

    return itemlist


def HomePage(item):
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")

# =================================================================
# Funzioni di servizio
# -----------------------------------------------------------------
def scrapedAll(url="", patron=""):
    matches = []
    headers = [
        ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0'],
        ['Referer',url]
    ]
    data = scrapertools.cache_page(url)
    data=data.replace('<span class="hdbox">HD</span>',"")
    #logger.info("data->"+data)
    xbmc.log("ok"+data)
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
    logger.info("elemento ->" + elemento)
    xbmc.log("elemento ->" + elemento)
    matches = re.compile(patron, re.DOTALL).findall(elemento)
    scrapertools.printMatches(matches)
    return matches
# =================================================================

HomeTxt = "[COLOR yellow]Torna Home[/COLOR]"
ThumbnailHome="https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Dynamic-blue-up.svg/580px-Dynamic-blue-up.svg.png"
ListTxt = "[COLOR orange]Torna a elenco principale [/COLOR]"
AvantiTxt = "[COLOR orange]Successivo>>[/COLOR]"
AvantiImg = "http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png"
ThumbPrimavisione="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"
FilmFanart="https://superrepo.org/static/images/fanart/original/script.artwork.downloader.jpg"
fanart="http://www.virgilioweb.it/wp-content/uploads/2015/06/film-streaming.jpg"
