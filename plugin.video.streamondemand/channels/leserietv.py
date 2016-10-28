# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para itafilmtv
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
#  By Costaplus
# ------------------------------------------------------------
import re
import urlparse

import xbmc
import xbmcgui

from core import config
from core import logger
from core import scrapertools
from core import downloadtools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "leserietv"
__category__ = "F"
__type__ = "generic"
__title__ = "leserie.tv"
__language__ = "IT"

DEBUG = config.get_setting("debug")

host = 'http://www.leserie.tv'

header = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', ('%s/streaming/' % host)]
]


def isGeneric():
    return True

# -----------------------------------------------------------------
def mainlist(item):
    logger.info("[leserietv.py] mainlist")
    itemlist = []
    itemlist.append(Item(channel=__channel__,
                         action="novita",
                         title="[COLOR yellow]Novità[/COLOR]",
                         url=("%s/streaming/" % host),
                         thumbnail="http://www.ilmioprofessionista.it/wp-content/uploads/2015/04/TVSeries3.png",
                         fanart=FilmFanart))

    itemlist.append(Item(channel=__channel__,
                         action="lista_serie",
                         title="[COLOR azure]Tutte le serie[/COLOR]",
                         url=("%s/streaming/" % host),
                         thumbnail="http://www.ilmioprofessionista.it/wp-content/uploads/2015/04/TVSeries3.png",
                         fanart=FilmFanart))

    itemlist.append(Item(channel=__channel__,
                         title="[COLOR azure]Categorie[/COLOR]",
                         action="categorias",
                         url=host,
                         thumbnail="https://farm8.staticflickr.com/7562/15516589868_13689936d0_o.png",
                         fanart=FilmFanart))


    itemlist.append(Item(channel=__channel__,
                         action="top50",
                         title="[COLOR azure]Top 50[/COLOR]",
                         url=("%s/top50.html" % host),
                         thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png",
                         fanart=FilmFanart))

    itemlist.append(Item(channel=__channel__,
                         action="search",
                         title="[COLOR orange]Cerca...[/COLOR][I](minimo 3 caratteri)[/I]",
                         thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search",
                         fanart=FilmFanart))

    itemlist.append(Item(channel=__channel__,
                         action="info",
                             title="[COLOR lime][I]Info canale[/I][/COLOR] [COLOR yellow]14/10/2016[/COLOR]",
                         thumbnail="http://www.mimediacenter.info/wp-content/uploads/2016/01/newlogo-final.png"))
    return itemlist


# =================================================================


# -----------------------------------------------------------------
def novita(item):
    logger.info("streamondemand.laserietv novità")
    itemlist = []

    data = scrapertools.cache_page(item.url)

    patron = '<div class="video-item-cover"[^<]+<a href="(.*?)">[^<]+<img src="(.*?)" alt="(.*?)">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedthumbnail = host + scrapedthumbnail
        logger.info("title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,viewmode="movie"), tipo='tv'))

    # Paginazione
    # ===========================================================
    patron = '<div class="pages">(.*?)</div>'
    paginazione = scrapertools.find_single_match(data, patron)
    patron = '<span>.*?</span>.*?href="([^"]+)".*?</a>'
    matches = re.compile(patron, re.DOTALL).findall(paginazione)
    scrapertools.printMatches(matches)
    # ===========================================================

    if len(matches) > 0:
        paginaurl = matches[0]
        itemlist.append(
            Item(channel=__channel__, action="novita", title="[COLOR orange]Successivo>>[/COLOR]", url=paginaurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))
        itemlist.append(
            Item(channel=__channel__, action="HomePage", title="[COLOR yellow]Torna Home[/COLOR]",thumbnail=ThumbnailHome, folder=True))
    return itemlist
# =================================================================

# -----------------------------------------------------------------
def lista_serie(item):
    logger.info("[leserie.py] lista_serie")
    itemlist = []

    post = "dlenewssortby=title&dledirection=asc&set_new_sort=dle_sort_cat&set_direction_sort=dle_direction_cat"

    data = scrapertools.cachePagePost(item.url, post=post)

    patron = '<div class="video-item-cover"[^<]+<a href="(.*?)">[^<]+<img src="(.*?)" alt="(.*?)">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedthumbnail = host + scrapedthumbnail
        logger.info(scrapedurl + " " + scrapedtitle + scrapedthumbnail)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,viewmode="movie"), tipo='tv'))

    # Paginazione
    # ===========================================================
    patron = '<div class="pages">(.*?)</div>'
    paginazione = scrapertools.find_single_match(data, patron)
    patron = '<span>.*?</span>.*?href="([^"]+)".*?</a>'
    matches = re.compile(patron, re.DOTALL).findall(paginazione)
    scrapertools.printMatches(matches)
    # ===========================================================

    if len(matches) > 0:
        paginaurl = matches[0]
        itemlist.append(
            Item(channel=__channel__, action="lista_serie", title="[COLOR orange]Successivo>>[/COLOR]", url=paginaurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))
        itemlist.append(
            Item(channel=__channel__, action="HomePage", title="[COLOR yellow]Torna Home[/COLOR]",thumbnail=ThumbnailHome, folder=True))
    return itemlist
# =================================================================

# -----------------------------------------------------------------
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
# =================================================================

# -----------------------------------------------------------------
def search(item, texto):
    logger.info("[laserietv.py] " + item.url + " search " + texto)
    itemlist = []
    url = "%s/index.php?do=search" % host
    post = "do=search&subaction=search&search_start=0&full_search=0&result_from=1&story=" + texto
    logger.debug(post)
    data = scrapertools.cachePagePost(url, post=post)

    patron = '<div class="video-item-cover"[^<]+<a href="(.*?)">[^<]+<img src="(.*?)" alt="(.*?)">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedthumbnail = host + scrapedthumbnail
        logger.info(scrapedurl + " " + scrapedtitle + scrapedthumbnail)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle), tipo='tv'))

    return itemlist
# =================================================================

# -----------------------------------------------------------------
def top50(item):
    logger.info("[laserietv.py] top50")
    itemlist = []

    data = scrapertools.cache_page(item.url)

    patron = 'class="top50item">\s*<[^>]+>\s*<.*?="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        scrapedthumbnail = ""
        logger.debug(scrapedurl + " " + scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,viewmode="movie"), tipo='tv'))

    return itemlist
# =================================================================

# -----------------------------------------------------------------
def episodios(item):
    logger.info("[leserietv.py] episodios")
    itemlist = []
    elenco = []
    data = scrapertools.cache_page(item.url)
    #xbmc.log("qua"+data)
    patron = '<li id[^<]+<[^<]+<.*?class="serie-title">(.*?)</span>[^>]+>[^<]+<.*?megadrive-(.*?)".*?data-link="([^"]+)">Megadrive</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedlongtitle,scrapedtitle, scrapedurl in matches:
        scrapedtitle = scrapedtitle.split('_')[0]+"x"+scrapedtitle.split('_')[1].zfill(2)

        elenco.append([scrapedtitle,scrapedlongtitle,scrapedurl])

        scrapedtitle = scrapedtitle + " [COLOR orange]" + scrapedlongtitle + "[/COLOR]"
        itemlist.append(Item(channel=__channel__,
                             action="findvideos",
                             title=scrapedtitle,
                             fulltitle=scrapedtitle,
                             url=scrapedurl,
                             thumbnail=item.thumbnail,
                             fanart=item.fanart if item.fanart != "" else item.scrapedthumbnail,
                             show=item.fulltitle))

    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title="Aggiungi alla liberia la serie",
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodios" + "###" + item.extra,
                 show=item.show))

    return itemlist
# =================================================================

#------------------------------------------------------------------
def play(item):
    itemlist=[]
    data = scrapertools.cache_page(item.url)

    elemento = scrapertools.find_single_match(data, 'config:{file:\'(.*?)\'')

    itemlist.append(Item(channel=__channel__,
                         action="play",
                         title=item.title,
                         url=elemento,
                         thumbnail=item.thumbnail,
                         fanart=item.fanart,
                         fulltitle=item.fulltitle,
                         show=item.fulltitle))
    return itemlist
# =================================================================

# -----------------------------------------------------------------
def info(item):
    itemlist = []

    dialog = xbmcgui.Dialog()
    linea1='[COLOR yellow]Servizi ripristinati:[/COLOR]'
    linea2='Aggiungi a libreria. '
    linea3='\n[COLOR orange]www.mimediacenter.info[/COLOR] - [I]pelisalacarta (For Italian users)[/I]'

    result=dialog.ok('Le serie TV Info',linea1,linea2,linea3)

    return mainlist(itemlist)
# =================================================================
# -----------------------------------------------------------------
def HomePage(item):
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")
# =================================================================


def test(item):
    itemlist=[]


    #for episodio,titolo,url in episodi:
     #   xbmc.log(titolo)
     #   downloadtools.downloadtitle(link(url),item.fulltitle + " " + episodio + " " + titolo)

    return itemlist


def link(url):
    data = scrapertools.cache_page(url)
    url = scrapertools.find_single_match(data, 'config:{file:\'(.*?)\'')

    return url

FilmFanart="https://superrepo.org/static/images/fanart/original/script.artwork.downloader.jpg"
ThumbnailHome="https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Dynamic-blue-up.svg/580px-Dynamic-blue-up.svg.png"

'''
itemlist.append(Item(channel=__channel__,
                     action="test",
                     title="Scarica tutta la serie [COLOR yellow]" + item.fulltitle + "[/COLOR]",
                     url=scrapedurl,
                     extra=elenco,
                     thumbnail=item.thumbnail,
                     fanart=item.fanart if item.fanart != "" else item.scrapedthumbnail,
                     fulltitle=item.fulltitle,
                     show=item.fulltitle))
'''