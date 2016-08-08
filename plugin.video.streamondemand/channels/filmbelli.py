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
import xbmc
from core import config
from core import logger
from core import scrapertools
from core.item import Item
from servers import servertools


__channel__ = "filmbelli"
__category__ = "F"
__type__ = "generic"
__title__ = "filmbelli.net"
__language__ = "IT"

DEBUG = config.get_setting("debug")

host = "http://www.filmbelli.net"

def isGeneric():
    return True

#-------------------------------------------------------------------------------------------------------------------------------------------
def mainlist(item):
    log("mainlist","init")
    itemlist =[]

    itemlist.append(Item(channel=__channel__, action="elenco", title="[COLOR yellow]Novità[/COLOR]"       , url=host                 , thumbnail=NovitaThumbnail, fanart=FilmFanart ))
    itemlist.append(Item(channel=__channel__, action="elenco", title="[COLOR azure]Film al Cinema[/COLOR]", url=host+"/genere/cinema", thumbnail=NovitaThumbnail, fanart=FilmFanart ))
    itemlist.append(Item(channel=__channel__, action="genere", title="[COLOR azure]Genere[/COLOR]"       , url=host                 , thumbnail=GenereThumbnail, fanart=FilmFanart ))
    itemlist.append(Item(channel=__channel__, action="search", title="[COLOR orange]Cerca..[/COLOR]"      ,url=host + "/?s="         , thumbnail=CercaThumbnail , fanart=FilmFanart))

    return itemlist
#===========================================================================================================================================

#-------------------------------------------------------------------------------------------------------------------------------------------
def genere(item):
    log("genere","init")
    itemlist = []

    patron ='<a href="(.*?)">(.*?)</a>'
    for scrapedurl, scrapedtitle in scrapedSingle(item.url, '<div class="tag_cloud_post_tag">(.*?)</div>',patron):
        log("genere", "title=[" + scrapedtitle + "] url=[" + scrapedurl + "]")
        itemlist.append(Item(channel=__channel__, action="elenco", title="[COLOR azure]"+ scrapedtitle+"[/COLOR]", url=scrapedurl,thumbnail=NovitaThumbnail, fanart=FilmFanart))

    return itemlist
#===========================================================================================================================================

#-------------------------------------------------------------------------------------------------------------------------------------------
def elenco(item):
    log("elenco","init")
    itemlist = []

    patron='class="bottom_line"></div>[^<]+<[^<]+<img.*?src="(.*?)"[^<]+</a>[^>]+<[^<]+<[^<]+<[^<]+<.*?class="movie_title"><a href="(.*?)">(.*?)</a>'
    for scrapedthumbnail,scrapedurl,scrapedtitle in scrapedSingle(item.url,'div id="movie_post_content">(.*?)</ul>',patron):
        scrapedtitle=scrapertools.decodeHtmlentities(scrapedtitle)
        log("elenco","title=["+ scrapedtitle + "] url=["+ scrapedurl +"] thumbnail=["+ scrapedthumbnail +"]")
        try:
            plot, fanart, poster, extrameta = info(scrapedtitle)
            itemlist.append(Item(channel=__channel__,
                                 thumbnail=poster,
                                 fanart=fanart if fanart != "" else poster,
                                 extrameta=extrameta,
                                 plot=str(plot),
                                 action="findvideos",
                                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                                 url=scrapedurl,
                                 fulltitle=scrapedtitle,
                                 show=scrapedtitle,
                                 folder=True))
        except:
            itemlist.append(Item(channel=__channel__,action="findvideos",title=scrapedtitle,url=scrapedurl,thumbnail=scrapedthumbnail,fulltitle=scrapedtitle,show=scrapedtitle))

    # Paginazione
    # ===========================================================================================================================
    matches=scrapedSingle(item.url,'class="vh-pages-wrapper span12 body-bg">(.*?)</div>','class="current">.*?</span><.*?href="(.*?)"')
    if len(matches) > 0:
        paginaurl = matches[0]
        itemlist.append(Item(channel=__channel__, action="elenco"  , title=AvantiTxt, url=paginaurl, thumbnail=AvantiImg))
        itemlist.append(Item(channel=__channel__, action="HomePage", title=HomeTxt  , folder=True))
    else:
        itemlist.append(Item(channel=__channel__, action="mainlist", title=ListTxt, folder=True))
    # ===========================================================================================================================
    return itemlist
#===========================================================================================================================================


#-------------------------------------------------------------------------------------------------------------------------------------------
def search(item,texto):
    log("search","init texto=["+ texto + "]")
    itemlist = []
    url=item.url+texto+"&search=Cerca+un+film"

    patron='class="bottom_line"></div>[^<]+<[^<]+<img.*?src="(.*?)"[^<]+</a>[^>]+<[^<]+<[^<]+<[^<]+<.*?class="movie_title"><a href="(.*?)">(.*?)</a>'
    for scrapedthumbnail,scrapedurl,scrapedtitle in scrapedSingle(url,'div id="movie_post_content">(.*?)</ul>',patron):
        scrapedtitle=scrapertools.decodeHtmlentities(scrapedtitle)
        log("novita","title=["+ scrapedtitle + "] url=["+ scrapedurl +"] thumbnail=["+ scrapedthumbnail +"]")
        try:
            plot, fanart, poster, extrameta = info(scrapedtitle)
            itemlist.append(Item(channel=__channel__,
                                 thumbnail=poster,
                                 fanart=fanart if fanart != "" else poster,
                                 extrameta=extrameta,
                                 plot=str(plot),
                                 action="findvideos",
                                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                                 url=scrapedurl,
                                 fulltitle=scrapedtitle,
                                 show=scrapedtitle,
                                 folder=True))
        except:
            itemlist.append(Item(channel=__channel__,action="findvideos",title=scrapedtitle,url=scrapedurl,thumbnail=scrapedthumbnail,fulltitle=scrapedtitle,show=scrapedtitle))

    # Paginazione
    # ===========================================================================================================================
    matches=scrapedSingle(url,'class="vh-pages-wrapper span12 body-bg">(.*?)</div>','class="current">.*?</span><.*?href="(.*?)"')
    if len(matches) > 0:
        paginaurl = scrapertools.decodeHtmlentities(matches[0])
        itemlist.append(Item(channel=__channel__, action="elenco"  , title=AvantiTxt, url=paginaurl, thumbnail=AvantiImg))
        itemlist.append(Item(channel=__channel__, action="HomePage", title=HomeTxt  , folder=True))
    else:
        itemlist.append(Item(channel=__channel__, action="mainlist", title= ListTxt, folder=True))
    # ============================================================================================================================
    return itemlist

#=================================================================
# Funzioni di servizio
#-----------------------------------------------------------------
def scrapedAll(url="",patron=""):
    matches = []
    data = scrapertools.cache_page(url)
    MyPatron = patron
    matches = re.compile(MyPatron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    return matches
#=================================================================

#-----------------------------------------------------------------
def scrapedSingle(url="",single="",patron=""):
    matches =[]
    data = scrapertools.cache_page(url)
    xbmc.log(data)
    elemento = scrapertools.find_single_match(data, single)
    log("scrapedSingle", "elemento:" + elemento)
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

#-----------------------------------------------------------------
def info(title):
    log("info","title=["+ title +"]")
    try:
        from core.tmdb import Tmdb
        oTmdb= Tmdb(texto_buscado=title, tipo= "movie", include_adult="false", idioma_busqueda="it")
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


#=================================================================
# riferimenti di servizio
#---------------------------------------------------------------------------------------------------------------------------------
NovitaThumbnail="https://superrepo.org/static/images/icons/original/xplugin.video.moviereleases.png.pagespeed.ic.j4bhi0Vp3d.png"
GenereThumbnail="https://farm8.staticflickr.com/7562/15516589868_13689936d0_o.png"
FilmFanart="https://superrepo.org/static/images/fanart/original/script.artwork.downloader.jpg"
CercaThumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"
CercaFanart="https://i.ytimg.com/vi/IAlbvyBdYdY/maxresdefault.jpg"
HomeTxt = "[COLOR yellow]Torna Home[/COLOR]"
ListTxt = "[COLOR orange]Torna a elenco principale [/COLOR]"
AvantiTxt="[COLOR orange]Successivo>>[/COLOR]"
AvantiImg="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png"
thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"
#----------------------------------------------------------------------------------------------------------------------------------