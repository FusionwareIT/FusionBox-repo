# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para animetubeita.com
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

__channel__ = "animetubeita"
__category__ = "F"
__type__ = "generic"
__title__ = "animetubeita.com"
__language__ = "IT"

DEBUG = config.get_setting("debug")


host = "http://www.animetubeita.com"
hostlista = host + "/lista-anime/"
hostgeneri= host + "/generi/"
hostcorso= host +"/category/serie-in-corso/"


def isGeneric():
    return True

#-----------------------------------------------------------------
def mainlist(item):
    log("animetubeita","mainlist")
    itemlist =[]
    itemlist.append(Item(channel=__channel__, action="lista_anime", title="[COLOR azure]Anime[/COLOR]",url=hostlista, thumbnail=AnimeThumbnail, fanart=AnimeFanart))
    itemlist.append(Item(channel=__channel__, action="lista_genere", title="[COLOR azure]Genere[/COLOR]", url=hostgeneri, thumbnail=CategoriaThumbnail, fanart=CategoriaFanart))
    itemlist.append(Item(channel=__channel__, action="dettaglio_genere", title="[COLOR azure]Serie in Corso[/COLOR]", url=hostcorso, thumbnail=CategoriaThumbnail, fanart=CategoriaFanart))
    return itemlist
#=================================================================

#-----------------------------------------------------------------
def lista_anime(item):
    log("animetubeita","lista_anime")

    itemlist =[]

    patron = '<li.*?class="page_.*?href="(.*?)">(.*?)</a></li>'
    for scrapedurl,scrapedtitle in scrapedAll(item.url, patron):
        title=scrapertools.decodeHtmlentities(scrapedtitle)
        title=title.split("Sub")[0]
        log("url:[" + scrapedurl + "] scrapedtitle:[" + title +"]")
        itemlist.append(Item(channel=__channel__, action="dettaglio", title="[COLOR azure]" + title + "[/COLOR]", url=scrapedurl,thumbnail="", fanart=""))

    return itemlist
#=================================================================

#-----------------------------------------------------------------
def lista_genere(item):
    log("animetubeita","lista_genere")

    itemlist =[]
    single= '<ul>(.*?)</ul>'
    patron = '<li class="cat-item[^<]+<.*?href="(.*?)".*?>(.*?)</a>'
    for scrapedurl, scrapedtitle in scrapedSingle(item.url,single,patron):
        title = scrapertools.decodeHtmlentities(scrapedtitle)
        log("url:[" + scrapedurl + "] scrapedtitle:[" + title + "]")
        itemlist.append(Item(channel=__channel__, action="dettaglio_genere", title="[COLOR azure]" + title + "[/COLOR]", url=scrapedurl,thumbnail="", fanart=""))


    return itemlist
#=================================================================

#-----------------------------------------------------------------
def dettaglio_genere(item):
    log("animetubeita","dettaglio")
    itemlist=[]

    patron='<h2 class="title"><a*.?href="(.*?)"[^>]+>(.*?)</a></h2>'
    for scrapedurl,scrapedtitle in scrapedAll(item.url,patron):
        log("url:[" + scrapedurl + "] scrapedtitle:[" + scrapedtitle + "]")
        title = scrapertools.decodeHtmlentities(scrapedtitle)
        title = title.split("Sub")[0]
        itemlist.append(Item(channel=__channel__, action="dettaglio", title="[COLOR azure]" + title + "[/COLOR]", url=scrapedurl, thumbnail="", fanart=""))
    return itemlist
#=================================================================

#-----------------------------------------------------------------
def dettaglio(item):
    log("animetubeita","dettaglio")

    itemlist =[]
    episodio=1
    patron='<tr[^<]+<[^<]+<strong>(.*?)</strong></td>[^<]+<[^<]+<.*?href="http://adf.ly.*?http://(.*?)"'
    #patron = '<tr[^<]+<[^<]+<strong>(.*?)</strong></td>[^<]+<[^<]+<[^<]+<img[^<]+<[^<]+[^>]+>[^<]+<td[^<]+<a href="http.*?http://(.*?)"[^<]+<img[^<]+</a></td>[^<]+</tr>'
    scrapedAll(item.url, patron)
    for scrapedtitle,scrapedurl in scrapedAll(item.url, patron):
        title= "Episodio "+ str(episodio)
        episodio+=1
        url = "http://"+scrapedurl
        log("url:[" + url + "  scrapedtitle:" + title +"]")
        itemlist.append(Item(channel=__channel__, action="play", title="[COLOR azure]" + title + "[/COLOR]", url=url,thumbnail="", fanart=""))

    return itemlist
#=================================================================


#=================================================================
# Funzioni di servizio
#-----------------------------------------------------------------
def scrapedAll(url="",patron=""):
    matches = []
    data = scrapertools.cache_page(url)
    if DEBUG: logger.info("data:"+data)
    MyPatron = patron
    matches = re.compile(MyPatron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    return matches
#=================================================================

#-----------------------------------------------------------------
def scrapedSingle(url="",single="",patron=""):
    matches =[]
    data = scrapertools.cache_page(url)
    elemento = scrapertools.find_single_match(data, single)
    matches = re.compile(patron, re.DOTALL).findall(elemento)
    scrapertools.printMatches(matches)

    return matches
#=================================================================

#-----------------------------------------------------------------
def log(funzione="",stringa="",canale=__channel__):
    if DEBUG:logger.info("[" + canale + "].[" + funzione + "] " + stringa)
#=================================================================

#-----------------------------------------------------------------
def HomePage(item):
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")
#=================================================================

#=================================================================
# riferimenti di servizio
#-----------------------------------------------------------------
AnimeThumbnail="http://img15.deviantart.net/f81c/i/2011/173/7/6/cursed_candies_anime_poster_by_careko-d3jnzg9.jpg"
AnimeFanart="http://www.animetubeita.com/wp-content/uploads/21407_anime_scenery.jpg"
CategoriaThumbnail="http://static.europosters.cz/image/750/poster/street-fighter-anime-i4817.jpg"
CategoriaFanart="http://www.animetubeita.com/wp-content/uploads/21407_anime_scenery.jpg"
CercaThumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"
CercaFanart="https://i.ytimg.com/vi/IAlbvyBdYdY/maxresdefault.jpg"
HomeTxt = "[COLOR yellow]Torna Home[/COLOR]"
AvantiTxt="[COLOR orange]Successivo>>[/COLOR]"
AvantiImg="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png"








