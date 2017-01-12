# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para itafilmtv
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#  By Costaplus
# ------------------------------------------------------------
import re
import xbmc
from core import config
from core import logger
from core import scrapertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "megafiletube"
__category__ = "F"
__type__ = "generic"
__title__ = "megafiletube.xyz"
__language__ = "IT"

DEBUG = config.get_setting("debug")

host = "http://megafiletube.xyz"
film =host + "/browse.php?search=&cat=1&t_lang=4"
cartoni=host +"/browse.php?search=&cat=13&t_lang=4"
serie=host + "/browse.php?search=&cat=14&t_lang=4"


def isGeneric():
    return True

#-----------------------------------------------------------------
def mainlist(item):
    logger.info("megafiletube mainlist")

    itemlist =[]
    itemlist.append(Item(channel=__channel__,action="elenco_film",title="[COLOR orange]Novità torrent [/COLOR][COLOR azure] Film[/COLOR]" ,url=film,thumbnail=thumbnovita,fanart=fanart))
    itemlist.append(Item(channel=__channel__,action="elenco_film",title="[COLOR orange]Novità torrent [/COLOR][COLOR azure] Serie[/COLOR]",url=serie,thumbnail=thumbnovita,fanart=fanart))
    itemlist.append(Item(channel=__channel__,action="elenco_film",title="[COLOR orange]Novità torrent [/COLOR][COLOR azure] Cartoni[/COLOR]",url=cartoni,thumbnail=thumbnovita,fanart=fanart))
    itemlist.append(Item(channel=__channel__,action="search",     title="[COLOR yellow]Cerca film...[/COLOR]",extra="movie", thumbnail=thumbcerca, fanart=fanart))

    return itemlist
#=================================================================

#-----------------------------------------------------------------
def elenco_film(item):
    logger.info("megafiletube elenco_film")
    itemlist=[]

    patron="href='magnet:?(.*?)'[^>]+>[^>]+>[^>]+>.*?img.*?src=.'(.*?)'.*?target='.*?'>(.*?)</a>"
    for scrapedurl,scrapedimg,scrapedtitolo in scrapedAll(item.url,patron):
        scrapedimg = scrapedimg.replace('\\','')
        base=scrapedtitolo.replace(".","")
        base=base.replace("(","")
        titolo=base.split("20")[0]

        itemlist.append(infoSod(Item(channel=__channel__,
                                     action="torrent",
                                     title="[COLOR darkkhaki].torrent [/COLOR]""[COLOR azure]"+scrapedtitolo+"[/COLOR]",
                                     fulltitle=scrapedtitolo,
                                     url=scrapedurl,
                                     thumbnail=scrapedimg,
                                     fanart=scrapedimg),
                                tipo="movie"))

    # Paginazione
    # ===========================================================
    pagina = scrapedAll(item.url, '<td class="highlight">.*?class="pager"><a.*?href="(.*?)"')
    if len(pagina) > 0:
        pagina=scrapertools.decodeHtmlentities(pagina[0])
        itemlist.append(Item(channel=__channel__, action="elenco_film", title=AvantiTxt, url=pagina,thumbnail=AvantiImg, folder=True))
        itemlist.append(Item(channel=__channel__, action="HomePage", title=HomeTxt,thumbnail=ThumbnailHome, folder=True))
    return itemlist
#=================================================================

#-----------------------------------------------------------------
def search(item,texto):
    logger.info("megafiletube search " + texto)

    itemlist = []

    item.url = "http://megafiletube.xyz/browse.php?search=" + texto + "&cat=0&t_lang=4"

    return elenco_film(item)
#=================================================================


#-----------------------------------------------------------------
def torrent(item):
    logger.info("megafiletube torrent")
    itemlist = []
    magnet = "magnet:"+item.url
    itemlist.append( Item(channel=__channel__, action="play", server="torrent", title=item.title , url=magnet , thumbnail=item.thumbnail , plot=item.plot , folder=False) )

    return itemlist
#=================================================================


#=================================================================
# Funzioni di servizio
#-----------------------------------------------------------------
def scrapedAll(url="",patron=""):
    matches = []
    data = scrapertools.cache_page(url)
    logger.info("data:"+data)
    MyPatron = patron
    matches = re.compile(MyPatron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    return matches
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
ThumbnailHome="https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Dynamic-blue-up.svg/580px-Dynamic-blue-up.svg.png"
