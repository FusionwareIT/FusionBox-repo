# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para animetubeita.com
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#  By Costaplus
# ------------------------------------------------------------
import re
import urllib

from core import config
from core import logger
from core import scrapertools
from core.item import Item

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
    itemlist.append(Item(channel=__channel__,
                         action="lista_home",
                         title="[COLOR azure]Home[/COLOR]",
                         url=host,
                         thumbnail=AnimeThumbnail,
                         fanart=AnimeFanart))
    itemlist.append(Item(channel=__channel__,
                         action="lista_anime",
                         title="[COLOR azure]A-Z[/COLOR]",
                         url=hostlista,
                         thumbnail=AnimeThumbnail,
                         fanart=AnimeFanart))
    itemlist.append(Item(channel=__channel__,
                         action="lista_genere",
                         title="[COLOR azure]Genere[/COLOR]",
                         url=hostgeneri,
                         thumbnail=CategoriaThumbnail,
                         fanart=CategoriaFanart))
    itemlist.append(Item(channel=__channel__,
                         action="lista_in_corso",
                         title="[COLOR azure]Serie in Corso[/COLOR]",
                         url=hostcorso,
                         thumbnail=CategoriaThumbnail,
                         fanart=CategoriaFanart))
    itemlist.append(Item(channel=__channel__,
                         action="search",
                         title="[COLOR lime]Cerca...[/COLOR]",
                         url=host+"/?s=",
                         thumbnail=CercaThumbnail,
                         fanart=CercaFanart))
    return itemlist
#=================================================================

#-----------------------------------------------------------------
def lista_home(item):
    log("animetubeita","lista_home")

    itemlist =[]

    patron = '<h2 class="title"><a href="(.*?)" rel="bookmark" title=".*?">.*?<img.*?src="(.*?)".*?<strong>Titolo</strong></td>.*?<td>(.*?)</td>.*?<td><strong>Trama</strong></td>.*?<td>(.*?)</'
    for scrapedurl,scrapedthumbnail,scrapedtitle,scrapedplot in scrapedAll(item.url, patron):
        title=scrapertools.decodeHtmlentities(scrapedtitle)
        title=title.split("Sub")[0]
        scrapedplot = scrapertools.decodeHtmlentities(scrapedplot)
        itemlist.append(Item(channel=__channel__,
                             action="dl_s",
                             title="[COLOR azure]" + title + "[/COLOR]",
                             url=scrapedurl,
                             thumbnail=scrapedthumbnail,
                             fanart=scrapedthumbnail,
                             plot=scrapedplot))

    # Paginazione
    # ===========================================================
    data = scrapertools.cache_page(item.url)
    patron = '<link rel="next" href="(.*?)"'
    next_page = scrapertools.find_single_match(data, patron)
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="lista_home",
                 title=AvantiTxt,
                 url=next_page,
                 thumbnail=AvantiImg,
                 folder=True))
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title=HomeTxt,
                 folder=True))
    # ===========================================================
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
        itemlist.append(Item(channel=__channel__,
                             action="dettaglio",
                             title="[COLOR azure]" + title + "[/COLOR]",
                             url=scrapedurl,
                             thumbnail="",
                             fanart=""))

    return itemlist
#=================================================================

#-----------------------------------------------------------------
def lista_genere(item):
    log("lista_anime_genere", "lista_genere")
    itemlist = []
 
    data = scrapertools.cache_page(item.url)
 
    bloque = scrapertools.get_match(data, '<div class="hentry page post-1 odd author-admin clear-block">(.*?)<div id="disqus_thread">')
 
    patron = '<li class="cat-item cat-item.*?"><a href="(.*?)" >(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)
 
    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="lista_generi",
                 title='[COLOR lightsalmon][B]' + scrapedtitle + '[/B][/COLOR]',
                 url=scrapedurl,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 thumbnail=item.thumbnail))
 
    return itemlist
#=================================================================

#-----------------------------------------------------------------
def lista_generi(item):
    log("animetubeita","lista_generi")

    itemlist =[]
    patron = '<h2 class="title"><a href="(.*?)" rel="bookmark" title=".*?">.*?<img.*?src="(.*?)".*?<strong>Titolo</strong></td>.*?<td>(.*?)</td>.*?<td><strong>Trama</strong></td>.*?<td>(.*?)</'
    for scrapedurl,scrapedthumbnail,scrapedtitle,scrapedplot in scrapedAll(item.url, patron):
        title=scrapertools.decodeHtmlentities(scrapedtitle)
        title=title.split("Sub")[0]
        scrapedplot = scrapertools.decodeHtmlentities(scrapedplot)
        itemlist.append(Item(channel=__channel__,
                             action="dettaglio",
                             title="[COLOR azure]" + title + "[/COLOR]",
                             url=scrapedurl,
                             thumbnail=scrapedthumbnail,
                             fanart=scrapedthumbnail,
                             plot=scrapedplot))

    # Paginazione
    # ===========================================================
    data = scrapertools.cache_page(item.url)
    patron = '<link rel="next" href="(.*?)"'
    next_page = scrapertools.find_single_match(data, patron)
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="lista_generi",
                 title=AvantiTxt,
                 url=next_page,
                 thumbnail=AvantiImg,
                 folder=True))
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title=HomeTxt,
                 folder=True))
    # ===========================================================


    return itemlist
#=================================================================

#-----------------------------------------------------------------
def lista_in_corso(item):
    log("animetubeita","lista_home")

    itemlist =[]

    patron = '<h2 class="title"><a href="(.*?)" rel="bookmark" title="Link.*?>(.*?)</a></h2>.*?<img.*?src="(.*?)".*?<td><strong>Trama</strong></td>.*?<td>(.*?)</td>'
    for scrapedurl,scrapedtitle,scrapedthumbnail,scrapedplot in scrapedAll(item.url, patron):
        title=scrapertools.decodeHtmlentities(scrapedtitle)
        title=title.split("Sub")[0]
        scrapedplot = scrapertools.decodeHtmlentities(scrapedplot)
        itemlist.append(Item(channel=__channel__,
                             action="dettaglio",
                             title="[COLOR azure]" + title + "[/COLOR]",
                             url=scrapedurl,
                             thumbnail=scrapedthumbnail,
                             fanart=scrapedthumbnail,
                             plot=scrapedplot))
    # Paginazione
    # ===========================================================
    data = scrapertools.cache_page(item.url)
    patron = '<link rel="next" href="(.*?)"'
    next_page = scrapertools.find_single_match(data, patron)
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="lista_genere",
                 title=AvantiTxt,
                 url=next_page,
                 thumbnail=AvantiImg,
                 folder=True))
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title=HomeTxt,
                 folder=True))
    # ===========================================================
    return itemlist
#=================================================================

#-----------------------------------------------------------------
def dl_s(item):
    log("animetubeita","dl_s")

    itemlist =[]
    encontrados = set()

    #1
    patron = '<p><center><a.*?href="(.*?)"'
    for scrapedurl in scrapedAll(item.url, patron):
        if scrapedurl in encontrados: continue
        encontrados.add(scrapedurl)
        title = "DOWNLOAD & STREAMING"
        itemlist.append(Item(channel=__channel__,
                             action="dettaglio",
                             title="[COLOR azure]" + title + "[/COLOR]",
                             url=scrapedurl,
                             thumbnail=item.thumbnail,
                             fanart=item.thumbnail,
                             plot=item.plot,
                             folder=True))
    #2
    patron = '<p><center>.*?<a.*?href="(.*?)"'
    for scrapedurl in scrapedAll(item.url, patron):
        if scrapedurl in encontrados: continue
        encontrados.add(scrapedurl)
        title = "DOWNLOAD & STREAMING"
        itemlist.append(Item(channel=__channel__,
                             action="dettaglio",
                             title="[COLOR azure]" + title + "[/COLOR]",
                             url=scrapedurl,
                             thumbnail=item.thumbnail,
                             fanart=item.thumbnail,
                             plot=item.plot,
                             folder=True))

    return itemlist
#=================================================================

#-----------------------------------------------------------------
def dettaglio(item):
    log("animetubeita","dettaglio")
    head = {'Referer': item.url,
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'}
    itemlist =[]
    episodio=1
    patron='<tr[^<]+?<[^<]+?<strong>(.*?)</strong></td>[^<]+?<[^<]+?<.*?href="http://.*?http://([^"]+?)"'
    scrapedAll(item.url, patron)
    for scrapedtitle,scrapedurl in scrapedAll(item.url, patron):
        title= "Episodio "+ str(episodio)
        episodio+=1
        url = "http://"+scrapedurl + '|' + urllib.urlencode(head)
        log("url:[" + url + "  scrapedtitle:" + title +"]")
        itemlist.append(Item(channel=__channel__,
                             action="play",
                             title="[COLOR azure]" + title + "[/COLOR]",
                             url=url,
                             thumbnail=item.thumbnail,
                             fanart=item.thumbnail,
                             plot=item.plot))

    return itemlist
#=================================================================

# -----------------------------------------------------------------
def search(item, texto):
    log("animetubeita", "search")
    item.url = item.url + texto
 
    try:
        return lista_home(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
 
 
# =================================================================

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
    import xbmc
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
