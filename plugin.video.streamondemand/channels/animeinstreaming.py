# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canale per http://animeinstreaming.net/
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------
import re
import urllib

import xbmc

from core import config
from core import logger
from core import scrapertools
from core.item import Item
from servers import adfly
from core import servertools

__channel__ = "animeinstreaming"
__category__ = "A"
__type__ = "generic"
__title__ = "AnimeInStreaming"
__language__ = "IT"

DEBUG = config.get_setting("debug")

host = "http://animeinstreaming.net/"

headers = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', host]
]


def isGeneric():
    return True


# -----------------------------------------------------------------
def mainlist(item):
    log("mainlist", "mainlist")
    itemlist = [Item(channel=__channel__,
                     action="lista_anime",
                     title="[COLOR azure]Anime [/COLOR]- [COLOR lightsalmon]Home[/COLOR]",
                     url=host,
                     thumbnail=AnimeThumbnail,
                     fanart=AnimeFanart),
                Item(channel=__channel__,
                     action="lista_anime_genere",
                     title="[COLOR azure]Anime [/COLOR]- [COLOR lightsalmon]Genere[/COLOR]",
                     url=host,
                     thumbnail=CategoriaThumbnail,
                     fanart=CategoriaFanart),
                Item(channel=__channel__,
                     action="lista_anime_anno",
                     title="[COLOR azure]Anime [/COLOR]- [COLOR lightsalmon]Anno[/COLOR]",
                     url=host,
                     thumbnail=CategoriaThumbnail,
                     fanart=CategoriaFanart),
                Item(channel=__channel__,
                     action="lista_anime_tutti",
                     title="[COLOR azure]Anime [/COLOR]- [COLOR lightsalmon]Lista Completa[/COLOR]",
                     url=host + "lista-anime/",
                     thumbnail=CategoriaThumbnail,
                     fanart=CategoriaFanart),
                Item(channel=__channel__,
                     action="lista_anime_lettera",
                     title="[COLOR azure]Anime [/COLOR]- [COLOR lightsalmon]Lista A-Z[/COLOR]",
                     url=host,
                     thumbnail=CategoriaThumbnail,
                     fanart=CategoriaFanart),
                Item(channel=__channel__,
                     action="search",
                     title="[COLOR lime]Cerca...[/COLOR]",
                     url="http://www.animeinstreaming.net/?s=",
                     thumbnail=CercaThumbnail,
                     fanart=CercaFanart)]

    return itemlist


# =================================================================

# -----------------------------------------------------------------
def lista_anime(item):
    log("lista_anime", "lista_anime")
    itemlist = []

    data = scrapertools.cache_page(item.url)

    patron = '<article id=.*?<a href="(.*?)" title="(.*?)">.*?<img.*?src="(.*?)".*?<div class="entry-content post-excerpt">(.*?)</div><!-- .entry-content -->'

    for scrapedurl, scrapedtitle, scrapedthumbnail, scrapedplot in scrapedAll(item.url, patron):
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = '[COLOR azure][B]' + scrapedtitle + '[/B][/COLOR]'
        scrapedplot = scrapertools.decodeHtmlentities(scrapedplot)

        itemlist.append(
            Item(channel=__channel__,
                 action="episodios",
                 title=scrapedtitle,
                 url=scrapedurl,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 plot=scrapedplot,
                 fanart=scrapedthumbnail,
                 thumbnail=scrapedthumbnail))

    # Paginazione
    # ===========================================================
    patron = '<a class="next page-numbers" href="(.*?)">.*? &#8250;</a></div>'
    next_page = scrapertools.find_single_match(data, patron)
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="lista_anime",
                 title=AvantiTxt,
                 url=next_page,
                 thumbnail=AvantiImg,
                 folder=True))
        itemlist.append(Item(channel=__channel__, action="HomePage", title=HomeTxt, folder=True))
    # ===========================================================
    return itemlist


# =================================================================

# -----------------------------------------------------------------
def lista_anime_genere(item):
    log("lista_anime_genere", "lista_anime_genere")
    itemlist = []

    data = scrapertools.cache_page(item.url)

    bloque = scrapertools.get_match(data, '<option value="-1">Anime per genere</option>(.*?)</select></td>')

    patron = '<option value="(.*?)">(.*?)</option>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url, scrapedtitle in matches:
        scrapedurl = host + url
        itemlist.append(
            Item(channel=__channel__,
                 action="lista_anime",
                 title='[COLOR lightsalmon][B]' + scrapedtitle + '[/B][/COLOR]',
                 url=scrapedurl,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 thumbnail=item.thumbnail))

    return itemlist


# =================================================================


# -----------------------------------------------------------------
def lista_anime_anno(item):
    log("lista_anime_anno", "lista_anime_anno")
    itemlist = []

    data = scrapertools.cache_page(item.url)

    bloque = scrapertools.get_match(data, '<option value="-1">Anime per anno</option>(.*?)</select></td>')

    patron = '<option value="(.*?)">(.*?)</option>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url, scrapedtitle in matches:
        scrapedurl = host + url
        itemlist.append(
            Item(channel=__channel__,
                 action="lista_anime",
                 title=scrapedtitle,
                 url=scrapedurl,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 thumbnail=item.thumbnail))

    return itemlist


# =================================================================

# -----------------------------------------------------------------
def lista_anime_tutti(item):
    log("lista_anime_lettera", "lista_anime_lettera")
    itemlist = []

    data = scrapertools.cache_page(item.url)

    bloque = scrapertools.get_match(data, '<ul class="su-posts su-posts-list-loop">(.*?)</ul>')

    patron = '<a href="(.*?)">(.*?)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(
            Item(channel=__channel__,
                 action="episodios",
                 title=scrapedtitle,
                 url=scrapedurl,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 thumbnail=item.thumbnail))

    return itemlist


# =================================================================

# -----------------------------------------------------------------
def lista_anime_lettera(item):
    log("lista_anime_lettera", "lista_anime_lettera")
    itemlist = []

    data = scrapertools.cache_page(item.url)

    bloque = scrapertools.get_match(data, '<option value="-1">Anime per lettera</option>(.*?)</select></td>')

    patron = '<option value="(.*?)">(.*?)</option>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url, scrapedtitle in matches:
        scrapedurl = host + url
        itemlist.append(
            Item(channel=__channel__,
                 action="lista_anime",
                 title=scrapedtitle,
                 url=scrapedurl,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 thumbnail=item.thumbnail))

    return itemlist


# =================================================================

# -----------------------------------------------------------------
def search(item, texto):
    log("lista_anime_categoria", "search")
    item.url = item.url + texto

    try:
        return lista_anime(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


# =================================================================

# -----------------------------------------------------------------
def episodios(item):
    itemlist = []

    encontrados = set()
    data = scrapertools.cache_page(item.url)

    # 1
    bloque = scrapertools.find_single_match(data, '<h4 style="text-align: center(.*?)</h4>')
    patron = '<a href="(.*?)" target="_blank">(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        if scrapedurl in encontrados: continue
        encontrados.add(scrapedurl)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = re.sub(r'<[^>]*?>', '', scrapedtitle)
        scrapedtitle = '[COLOR azure][B]' + scrapedtitle + '[/B][/COLOR]'
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideo",
                 title=scrapedtitle,
                 url=scrapedurl,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 plot=item.plot,
                 fanart=item.thumbnail,
                 thumbnail=item.thumbnail))
    # 2
    patron = '<strong><a href="(.*?)" target="_blank">([^<]+)<.*?a></strong>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        if scrapedurl in encontrados: continue
        encontrados.add(scrapedurl)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = re.sub(r'<[^>]*?>', '', scrapedtitle)
        scrapedtitle = '[COLOR pink][B]' + scrapedtitle + '[/B][/COLOR]'
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideo",
                 title=scrapedtitle,
                 url=scrapedurl,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 plot=item.plot,
                 fanart=item.thumbnail,
                 thumbnail=item.thumbnail))
    # 3
    patron = '<a style="color: #ff0000;" href="(.*?)" target="_blank">(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        if scrapedurl in encontrados: continue
        encontrados.add(scrapedurl)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = re.sub(r'<[^>]*?>', '', scrapedtitle)
        scrapedtitle = '[COLOR greenyellow][B]' + scrapedtitle + '[/B][/COLOR]'
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideo",
                 title=scrapedtitle,
                 url=scrapedurl,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 plot=item.plot,
                 fanart=item.thumbnail,
                 thumbnail=item.thumbnail))
    # 4
    patron = '<h4 style="text-align: center;"><a href="(.*?)" target="_blank"><strong>(.*?)</b>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        if scrapedurl in encontrados: continue
        encontrados.add(scrapedurl)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = re.sub(r'<[^>]*?>', '', scrapedtitle)
        scrapedtitle = '[COLOR cyan][B]' + scrapedtitle + '[/B][/COLOR]'
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideo",
                 title=scrapedtitle,
                 url=scrapedurl,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 plot=item.plot,
                 fanart=item.thumbnail,
                 thumbnail=item.thumbnail))

    # 5 - mob psycho 100
    patron = '<h4 style="text-align: center;".*?<a href="(.*?)" target="_blank">(.*?)</h4>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        if scrapedurl in encontrados: continue
        encontrados.add(scrapedurl)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = re.sub(r'<[^>]*?>', '', scrapedtitle)
        scrapedtitle = '[COLOR bisque][B]' + scrapedtitle + '[/B][/COLOR]'
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideo",
                 title=scrapedtitle,
                 url=scrapedurl,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 plot=item.plot,
                 fanart=item.thumbnail,
                 thumbnail=item.thumbnail))

    # Comandi di servizio
    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title="Aggiungi " + item.title + " alla libreria",
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodios",
                 show=item.show))
        itemlist.append(
            Item(channel=item.channel,
                 title="Scarica tutti gli episodi della serie",
                 url=item.url,
                 action="download_all_episodes",
                 extra="episodios",
                 show=item.show))

    return itemlist


# ==================================================================

# -----------------------------------------------------------------
def findvideo(item):
    logger.info("streamondemand.animeinstreaming play")

    itemlist = []

    url = item.url
    if 'adf.ly' in item.url:
        url = adfly.get_long_url(item.url)

    if 'animeforce' in url:
        url = url.split('&')[0]
        headers.append(['Referer', item.url])
        data = scrapertools.cache_page(url, headers=headers)
        patron = """<source\s*src=(?:"|')([^"']+?)(?:"|')\s*type=(?:"|')video/mp4(?:"|')>"""
        matches = re.compile(patron, re.DOTALL).findall(data)
        headers.append(['Referer', url])
        for video in matches:
            itemlist.append(Item(channel=__channel__, action="play", title=item.title, url=video + '|' + urllib.urlencode(dict(headers)), folder=False))
    else:
        itemlist.extend(servertools.find_video_items(data=url))

        for videoitem in itemlist:
            videoitem.title = item.title + videoitem.title
            videoitem.fulltitle = item.fulltitle
            videoitem.show = item.show
            videoitem.thumbnail = item.thumbnail
            videoitem.channel = __channel__

    return itemlist


# ==================================================================

# =================================================================
# Funzioni di servizio
# -----------------------------------------------------------------
def scrapedAll(url="", patron=""):
    data = scrapertools.cache_page(url)
    if DEBUG: logger.info("data:" + data)
    MyPatron = patron
    matches = re.compile(MyPatron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    return matches


# =================================================================

# -----------------------------------------------------------------
def scrapedSingle(url="", single="", patron=""):
    data = scrapertools.cache_page(url)
    paginazione = scrapertools.find_single_match(data, single)
    matches = re.compile(patron, re.DOTALL).findall(paginazione)
    scrapertools.printMatches(matches)

    return matches


# =================================================================

# -----------------------------------------------------------------
def Crea_Url(pagina="1", azione="ricerca", categoria="", nome=""):
    # esempio
    # chiamate.php?azione=ricerca&cat=&nome=&pag=
    Stringa = host + "chiamate.php?azione=" + azione + "&cat=" + categoria + "&nome=" + nome + "&pag=" + pagina
    log("crea_Url", Stringa)
    return Stringa


# =================================================================

# -----------------------------------------------------------------
def log(funzione="", stringa="", canale=__channel__):
    if DEBUG: logger.info("[" + canale + "].[" + funzione + "] " + stringa)


# =================================================================

# -----------------------------------------------------------------
def HomePage(item):
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")


# =================================================================

# =================================================================
# riferimenti di servizio
# -----------------------------------------------------------------
AnimeThumbnail = "http://img15.deviantart.net/f81c/i/2011/173/7/6/cursed_candies_anime_poster_by_careko-d3jnzg9.jpg"
AnimeFanart = "https://i.ytimg.com/vi/IAlbvyBdYdY/maxresdefault.jpg"
CategoriaThumbnail = "http://static.europosters.cz/image/750/poster/street-fighter-anime-i4817.jpg"
CategoriaFanart = "https://i.ytimg.com/vi/IAlbvyBdYdY/maxresdefault.jpg"
CercaThumbnail = "http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"
CercaFanart = "https://i.ytimg.com/vi/IAlbvyBdYdY/maxresdefault.jpg"
HomeTxt = "[COLOR yellow]Torna Home[/COLOR]"
AvantiTxt = "[COLOR orange]Successivo>>[/COLOR]"
AvantiImg = "http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png"
