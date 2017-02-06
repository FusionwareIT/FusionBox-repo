# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# fusionse.- XBMC Plugin
# Canal per filmhdstreaming
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#  By Costaplus
# ------------------------------------------------------------

#   Import  sono importanti per il funzionamento del canale
import re
import urlparse

from core import config
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "filmhdstreaming"
__category__ = "F"
__type__ = "generic"
__title__ = "filmhdstreaming (IT)"
__language__ = "IT"

# riferimento alla gestione del log
DEBUG = config.get_setting("debug")

host = "http://filmhdstreaming.org"

# -----------------------------------------------------------------
# Elenco inziale del canale
def mainlist(item):
    logger.info("filmhdstreaming mainlist")

    itemlist = []
    #itemlist.append(Item(channel=item.channel, action="elenco_ten", title="[COLOR yellow]Film Top 10[/COLOR]", url=host,thumbnail=NovitaThumbnail, fanart=fanart))
    #itemlist.append(Item(channel=item.channel, action="elenco_top", title="[COLOR azure]Film Top[/COLOR]", url=host,thumbnail=NovitaThumbnail, fanart=fanart))
    itemlist.append(Item(channel=item.channel, action="elenco", title="[COLOR azure]Aggiornamenti Film[/COLOR]", url=host+"/page/1.html",thumbnail=NovitaThumbnail, fanart=fanart))
    itemlist.append(Item(channel=item.channel, action="elenco_genere", title="[COLOR azure]Film per Genere[/COLOR]", url=host,thumbnail=GenereThumbnail, fanart=fanart))
    itemlist.append(Item(channel=item.channel, action="search", title="[COLOR orange]Cerca film...[/COLOR]", extra="movie",thumbnail=thumbcerca, fanart=fanart))

    return itemlist
# =================================================================

#------------------------------------------------------------------
# Funzione elenco top
def elenco_top(item):
    logger.info("filmhdstreaming elenco_top")

    itemlist = []

    data = scrapertools.cache_page(item.url)

    # metodo che utilizzo pee verificare cosa scarica nella chace
    # provate and andare nel log di kodi e controllate in fondo...
    # io uso notepad ++ che ha come vantaggio di auto aggiornarsi ad ogni cambiamento del file
    # per non stare ad aprire e chidere tutte le vole il file di log di kodi
    logger.info("ecco la pagina completa ->" + data)

    # nel patron in questo caso tutto ciò che è tra > e class= verrà preso in cosiderazione
    patron = 'id="box_movies1">(.*?)class="header_slider">'
    filtro_top = scrapertools.find_single_match(data, patron)

    # controllo log
    logger.info("filtrato ->" + filtro_top)

    patron = 'class="movie">[^>]+><a href="(.*?)"><img src="(.*?)".*?<h2>(.*?)<\/h2>'

    matches = scrapertools.find_multiple_matches(filtro_top, patron)

    for scrapedurl, scrapedimg, scrapedtitle in matches:
        # sempre per controllare il log
        logger.info("Url:" + scrapedurl + " thumbnail:" + scrapedimg + " title:" + scrapedtitle)
        title = scrapedtitle.split("(")[0]
        itemlist.append(infoSod(Item(channel=item.channel,
                             action="findvideos",
                             title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                             fulltitle=scrapedtitle,
                             url=scrapedurl,
                             thumbnail=scrapedimg,
                             fanart=""
                             )))

    return itemlist
# =================================================================

#------------------------------------------------------------------
# Funzione elenco top
def elenco(item):
    logger.info("filmhdstreaming elenco")

    itemlist = []
    data = scrapertools.cache_page(item.url)

    patron = '_b2"><a href="([^"]+)" title="(.*?)"><img src="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedplot = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = scrapedtitle.replace(" streaming ita", "")
        scrapedtitle = scrapedtitle.replace(" film streaming", "")
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
    patronvideos = '<a class="page dark gradient" href="(.*?)">Avanti'
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
                 action="elenco",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))

    return itemlist

# =================================================================


#------------------------------------------------------------------
# Funzione elenco genere
def elenco_genere(item):
    logger.info("filmhdstreaming elenco_genere")

    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    bloque = scrapertools.get_match(data, '<ul>(.*?)</ul>')

    # Extrae las entradas (carpetas)
    patron = '<li><a href="(.*?)"><i class=[^s]+strong>(.*?)<\/strong><\/a><\/li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapedtitle.replace("Film streaming ", "")
        if DEBUG: logger.info("title=[" + scrapedtitle + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="elenco",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png",
                 folder=True))

    return itemlist

#==================================================================

#------------------------------------------------------------------
# Funzione elenco genere
def elenco_ten(item):
    logger.info("filmhdstreaming elenco_ten")

    itemlist = []
    data = scrapertools.cache_page(item.url)
    patron = '<ul class="lista">(.*?)</ul>'

    filtro= scrapertools.find_single_match(data, patron)
    patron = '<li>.*?href="(.*?)">(.*?)</a>'
    matches = scrapertools.find_multiple_matches(filtro, patron)

    for scrapedurl,scrapedtitle in matches:
        logger.info("Url:" + scrapedurl + " title:" + scrapedtitle)
        itemlist.append(infoSod(Item(channel=item.channel,
                             action="findvideos",
                             title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                             fulltitle=scrapedtitle,
                             url=scrapedurl,
                             thumbnail="",
                             fanart=""
                             )))

    return itemlist
#==================================================================


#------------------------------------------------------------------
def search(item, texto):
    logger.info("filmhdstreaming search " + texto)

    itemlist = []

    item.url = "http://filmhdstreaming.net/tag/" + texto + "/"

    try:
        return elenco(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

#------------------------------------------------------------------

########################################################################
# Riferimenti a immagini statiche
GenereThumbnail = "https://farm8.staticflickr.com/7562/15516589868_13689936d0_o.png"
NovitaThumbnail = "https://superrepo.org/static/images/icons/original/xplugin.video.moviereleases.png.pagespeed.ic.j4bhi0Vp3d.png"
thumbcerca = "http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"
fanart ="https://superrepo.org/static/images/fanart/original/script.artwork.downloader.jpg"
HomeTxt = "[COLOR yellow]Torna Home[/COLOR]"
AvantiTxt = "[COLOR orange]Successivo>>[/COLOR]"
AvantiImg = "http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png"
ThumbnailHome = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Dynamic-blue-up.svg/580px-Dynamic-blue-up.svg.png"
thumbnovita = "http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"
