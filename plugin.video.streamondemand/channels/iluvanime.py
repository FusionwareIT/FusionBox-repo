# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para animestream.it
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#  By Costaplus
# ------------------------------------------------------------
import re
import urlparse

from core import config
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item

__channel__ = "iluvanime"
__category__ = "F,A"
__type__ = "generic"
__title__ = "iluvanime.net"
__language__ = "IT"

DEBUG = config.get_setting("debug")

host = "http://www.iluvanime.net"

def isGeneric():
    return True

# -----------------------------------------------------------------
def mainlist(item):
    logger.info("streamondemand.iluvanime mainlist")

    itemlist = []
    itemlist.append(Item(channel=__channel__, action="lista_ultimi", title="[COLOR azure]Ultimi Episodi[/COLOR]", url=host, thumbnail=AnimeThumbnail, fanart=AnimeFanart))
    itemlist.append(Item(channel=__channel__, action="lista_anime", title="[COLOR azure]Lista Anime[/COLOR]", url=host+"/listaserie.php", thumbnail=AnimeThumbnail, fanart=AnimeFanart))

    return itemlist
# =================================================================

# -----------------------------------------------------------------
def lista_ultimi(item):
    logger.info("streamondemand.iluvanime lista_ultimi")
    itemlist = []
    patron = '<a class="linksection" href="(.*?)"[^<]+<[^<]+<img.*?src="(.*?)".*?title="(.*?)"[^<]+<[^<]+<[^<]+<h4>(.*?)</h4>'
    for scrapedurl, scrapedthumbnail, scrapedtitle,scrapedepisodio in scrapedSingle(item.url,'<div class="areacentrale">(.*?)<div class="footer">', patron):
        logger.info("scrapedurl: " + scrapedurl + " scrapedthumbnail:" + scrapedthumbnail + "scrapedtitle:" + scrapedtitle +" scrapedepisodio:" + scrapedepisodio)
        title=scrapedtitle + " [COLOR orange]"+ scrapedepisodio+"[/COLOR] "
        itemlist.append(
            Item(channel=__channel__,
                 action="episodios",
                 title=title,
                 url=urlparse.urljoin(host,"/"+scrapedurl),
                 thumbnail=urlparse.urljoin(host, scrapedthumbnail),
                 fulltitle=title,
                 show=title,
                 fanart=""))

    return itemlist

# -----------------------------------------------------------------
def lista_anime(item):
    logger.info("streamondemand.iluvanime lista_anime")
    itemlist = []

    patron = '<a href="(.*?)" class="linksection">[^<]+<[^<]+<img.*?src="(.*?)"[^<]+<[^<]+<h2>(.*?)</h2>'
    for scrapedurl, scrapedthumbnail, scrapedtitle in scrapedSingle(item.url,'<div class="areacentrale">(.*?)<div class="footer">', patron):
        logger.info("scrapedurl: " + scrapedurl + " scrapedthumbnail:" + scrapedthumbnail + "scrapedtitle:" + scrapedtitle)
        itemlist.append(
            Item(channel=__channel__,
                 action="episodios",
                 title=scrapedtitle,
                 url=urlparse.urljoin(host,"/"+scrapedurl),
                 thumbnail=urlparse.urljoin(host, scrapedthumbnail),
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 fanart=""))

    return itemlist
# =================================================================

# -----------------------------------------------------------------
def episodios(item):
    logger.info("streamondemand.iluvanime episodios")
    itemlist = []
    patron = '<a class="linksection" href="(.*?)">[^<]+<[^<]+<[^<]+<.*?class="desfilmato">(.*?)</p>'
    for scrapedurl, scrapedtitle in scrapedAll(item.url, patron):
        logger.info("scrapedurl: " + scrapedurl + " scrapedtitle:" + scrapedtitle)
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 fulltitle=scrapedtitle,
                 fanart=""))

    return itemlist
# =================================================================

# -----------------------------------------------------------------
def findvideos(item):
    logger.info("streamondemand.iluvanime play")

    itemlist = []

    url = 'http://www' + item.url.split('www')[1]
    head = [['Upgrade-Insecure-Requests', '1'],
            ['User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0']]
    data = scrapertools.cache_page(url, headers=head)

    patron = '<source.*?src="(.*?)".*?type=\'video/mp4\''
    matches = re.compile(patron, re.DOTALL).findall(data)
    for video in matches:
        itemlist.append(Item(action="play", url=video))

    itemlist.extend(servertools.find_video_items(data=data))
    for videoitem in itemlist:
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist
# ==================================================================


# =================================================================
# Funzioni di servizio
# -----------------------------------------------------------------
def scrapedAll(url="", patron=""):

    data = scrapertools.cache_page(url)
    MyPatron = patron
    matches = re.compile(MyPatron, re.DOTALL).findall(data)

    return matches
# =================================================================

#-----------------------------------------------------------------
def scrapedSingle(url="",single="",patron=""):
    data = scrapertools.cache_page(url)
    elemento = scrapertools.find_single_match(data, single)
    matches = re.compile(patron, re.DOTALL).findall(elemento)

    return matches
#=================================================================

# =================================================================
# riferimenti di servizio
# -----------------------------------------------------------------
AnimeThumbnail = "http://img15.deviantart.net/f81c/i/2011/173/7/6/cursed_candies_anime_poster_by_careko-d3jnzg9.jpg"
AnimeFanart = "https://superrepo.org/static/images/fanart/original/plugin.video.animeram.jpg"


