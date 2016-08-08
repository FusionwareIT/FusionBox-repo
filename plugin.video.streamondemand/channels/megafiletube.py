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
import filmontv

__channel__ = "megafiletube"
__category__ = "F"
__type__ = "generic"
__title__ = "megafiletube.xyz"
__language__ = "IT"

DEBUG = config.get_setting("debug")

host = "http://megafiletube.xyz"
film =host + "/browse.php?search=&cat=1&t_lang=4"

def isGeneric():
    return True

#-----------------------------------------------------------------
def mainlist(item):
    log("mainlist","mainlist")
    itemlist =[]
    itemlist.append(Item(channel=__channel__,action="elenco_film",title="[COLOR azure]Novità Film[/COLOR]"    ,url=film    ,thumbnail=thumbnovita,fanart=fanart))
    itemlist.append(Item(channel=__channel__, title="[COLOR yellow]Cerca...[/COLOR]", action="search",thumbnail=thumbcerca,fanart=fanart))

    return itemlist
#=================================================================

#-----------------------------------------------------------------
def elenco_film(item):
    log("elenco_film", "elenco_film")
    itemlist=[]

    patron="img.*?src=.'(.*?)'.*?href=\"(.*?)\"[^>]+>(.*?)</a>"
    for scrapedimg,scrapedurl,scrapedtitolo in scrapedAll(item.url,patron):
        scrapedimg = scrapedimg.replace('\\','')
        base=scrapedtitolo.replace(".","")
        base=base.replace("(","")
        titolo=base.split("20")[0]
        itemlist.append(Item(channel=__channel__, action="dettaglio_film", title="[COLOR darkkhaki].torrent [/COLOR]""[COLOR azure]"+titolo+"[/COLOR]",fulltitle=scrapedtitolo, url=host+scrapedurl,thumbnail=scrapedimg, fanart=scrapedimg))

    # Paginazione
    # ===========================================================
    pagina = scrapedAll(item.url, '<td class="highlight">.*?class="pager"><a.*?href="(.*?)"')
    if len(pagina) > 0:
        pagina=scrapertools.decodeHtmlentities(pagina[0])
        log("megafiletube", "Pagina url: " + pagina)
        itemlist.append(Item(channel=__channel__, action="elenco_film", title=AvantiTxt, url=pagina,thumbnail=AvantiImg, folder=True))
        itemlist.append(Item(channel=__channel__, action="HomePage", title=HomeTxt, folder=True))
    return itemlist
#=================================================================

#-----------------------------------------------------------------
def dettaglio_film(item):
    log("dettaglio_film", "dettaglio_film")
    itemlist=[]

    #patronMagnet = "red3'>.*?<div class='icon3'>.*?href=\"(.*?)\".*?class='fa fa-magnet"
    patronMagnet = '<div class=\'icon3\'> <a href="(magnet[^&]+)[^>]+>'
    patronMagnet = patronMagnet.replace("&amp;","&")
    titolo=scrapedAll(item.url, patronMagnet)

    patronTorrent = "<div class='icon3'>.*?href=\"(.*?)\".*?class='fa fa-download"
    torrent =scrapedAll(item.url,patronTorrent)

    patronTriler='<embed.*?src=\'(.*?)\''
    Triler = scrapedAll(item.url,patronTriler)

    xbmc.log("titolo " + titolo[0] + "torrent " + torrent[0] + " " + Triler[0] )

    itemlist.append(Item(channel=__channel__, action="torrent", title="[COLOR yellow] Torrent [/COLOR] - [COLOR azure]Download[/COLOR] [I](" + host+torrent[0]+ ")[/I]",url=host+torrent[0], folder=True))
    itemlist.append(Item(channel=__channel__, action="torrent",server="torrent", title="[COLOR yellow] Magnet [/COLOR] - [COLOR azure]Streaming[/COLOR] [I](" + titolo[0] + ")[/I]",url=titolo[0], folder=True))
    itemlist.append(Item(channel=__channel__, action="findvideos", title="[COLOR yellow]Trailer [/COLOR]", url=item.url,folder=True))
    itemlist.append(Item(channel=__channel__, action="cerca", title="[COLOR orange]Cerca in tutti i canali [/COLOR] "+ item.title, folder=True))
    itemlist.append(Item(channel=__channel__,action="",title="[COLOR azure]Info Qualità:[/COLOR] [I]"+ item.fulltitle + "[/I]",folder=False))
    return itemlist
#=================================================================

#-----------------------------------------------------------------
def search(item,texto):
    log("serach","search " + texto)
    itemlist = []
    item.url = host+"/browse.php?search=" + texto +"&cat=1&t_lang=4"
    return elenco_film(item)
#=================================================================

#-----------------------------------------------------------------
def cerca(item):
    itemlist=[]
    item.title=item.title.replace("[COLOR orange]Cerca nei canali [/COLOR]","")
    xbmc.log("titolo:"+item.title)
    itemlist=filmontv.do_search(item)
    if len(itemlist)==0:
        itemlist.append(Item(channel=__channel__,action="mainlist",title="[COLOR red]Nessun canale dispone di questo titolo![/COLOR]"))
    return itemlist
#=================================================================

#-----------------------------------------------------------------
def torrent(item):
    logger.info("[corsaronero.py] play")
    itemlist = []

    itemlist.append( Item(channel=__channel__, action="play", server="torrent", title=item.title , url=item.url , thumbnail=item.thumbnail , plot=item.plot , folder=False) )

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
def log(funzione="",stringa="",canale=__channel__):
    if DEBUG:logger.info("[" + canale + "].[" + funzione + "] " + stringa)
#=================================================================

#-----------------------------------------------------------------
def HomePage(item):
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")
#=================================================================

thumbnovita="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"
thumbcerca="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"
fanart="http://www.virgilioweb.it/wp-content/uploads/2015/06/film-streaming.jpg"
HomeTxt = "[COLOR yellow]Torna Home[/COLOR]"
AvantiTxt="[COLOR orange]Successivo>>[/COLOR]"
AvantiImg="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png"
