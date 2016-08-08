# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para casacinema
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
# ------------------------------------------------------------
import re
import sys
import time
import urllib2
import urlparse

from core import logger
from core import config
from core import scrapertools
from servers import servertools
from core.item import Item

__channel__ = "casacinema"
__category__ = "F,S,A"
__type__ = "generic"
__title__ = "casacinema"
__language__ = "IT"

host = "http://www.casa-cinema.org"

headers = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', 'http://www.casa-cinema.org/genere/serie-tv'],
    ['Connection', 'keep-alive']


]
def isGeneric():
    return True


def mainlist(item):
    logger.info("streamondemand.casacinema mainlist")

    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film - Novita'[/COLOR]",
                     action="peliculas",
                     extra="film",
                     url="%s/genere/film" % host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film - HD[/COLOR]",
                     action="peliculas",
                     url="%s/?s=[HD]" % host,
                     thumbnail="http://jcrent.com/apple%20tv%20final/HD.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Categorie[/COLOR]",
                     action="categorias",
                     url=host,
                     thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/All%20Movies%20by%20Genre.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film Sub - Ita[/COLOR]",
                     action="peliculas",
                     url="%s/genere/sub-ita" % host,
                     thumbnail="http://i.imgur.com/qUENzxl.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[/COLOR]",
                     extra="serie",
                     action="peliculas_tv",
                     url="%s/genere/serie-tv" % host,
                     thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/New%20TV%20Shows.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Serie TV...[/COLOR]",
                     action="search",
                     extra="serie",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist


def search(item, texto):
    logger.info("[casacinema.py] " + item.url + " search " + texto)

    item.url = host + "?s=" + texto

    try:
        if item.extra == "serie":
            return peliculas_tv(item)
        else:
            return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def peliculas(item):
    logger.info("streamondemand.casacinema peliculas")

    itemlist = []

    # Descarga la pagina
    data = anti_cloudflare(item.url)

    # Extrae las entradas (carpetas)
    patron = '<div class="box-single-movies">\s*'
    patron += '<a href="([^>"]+)".*?title="([^>"]+)" >.*?<img class.*?<img.*?src="([^>"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        title = scrapertools.decodeHtmlentities(scrapedtitle)
        html = scrapertools.cache_page(scrapedurl)
        start = html.find("<div class=\"row content-post\" >")
        end = html.find("<a class=\"addthis_button_facebook_like\" fb:like:layout=\"button_count\"></a>", start)
        scrapedplot = html[start:end]
        scrapedplot = re.sub(r'<[^>]*>', '', scrapedplot)
        scrapedplot = scrapertools.decodeHtmlentities(scrapedplot).strip()
        tmdbtitle = title.split("[")[0]
        try:
           plot, fanart, poster, extrameta = info(tmdbtitle)

           itemlist.append(
               Item(channel=__channel__,
                    thumbnail=poster,
                    fanart=fanart if fanart != "" else poster,
                    extrameta=extrameta,
                    plot=str(plot),
                    action="episodios" if item.extra == "serie" else "findvideos",
                    title=title,
                    url=scrapedurl,
                    fulltitle=title,
                    show=title,
                    folder=True))
        except:
           itemlist.append(
               Item(channel=__channel__,
                    action="episodios" if item.extra == "serie" else "findvideos",
                    title=title,
                    url=scrapedurl,
                    thumbnail=scrapedthumbnail,
                    fulltitle=title,
                    show=title,
                    plot=scrapedplot,
                    folder=True))

    ## Paginación
    next_page = scrapertools.find_single_match(data, 'rel="next" href="([^"]+)"')

    if next_page != "":
        itemlist.append(
                Item(channel=__channel__,
                     action="HomePage",
                     title="[COLOR yellow]Torna Home[/COLOR]",
                     folder=True)),
        itemlist.append(
                Item(channel=__channel__,
                     action="peliculas",
                     title="[COLOR orange]Successivo >>[/COLOR]",
                     url=next_page,
                     thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png"))

    return itemlist

def peliculas_tv(item):
    logger.info("streamondemand.casacinema peliculas")

    itemlist = []

    # Descarga la pagina
    data = anti_cloudflare(item.url)

    # Extrae las entradas (carpetas)
    patron = '<div class="box-single-movies">\s*'
    patron += '<a href="([^>"]+)".*?title="([^>"]+)" >.*?<img class.*?<img.*?src="([^>"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        title = scrapertools.decodeHtmlentities(scrapedtitle)
        html = scrapertools.cache_page(scrapedurl)
        start = html.find("<div class=\"row content-post\" >")
        end = html.find("<a class=\"addthis_button_facebook_like\" fb:like:layout=\"button_count\"></a>", start)
        scrapedplot = html[start:end]
        scrapedplot = re.sub(r'<[^>]*>', '', scrapedplot)
        scrapedplot = scrapertools.decodeHtmlentities(scrapedplot).strip()
        tmdbtitle = title.split("Serie")[0]
        try:
           plot, fanart, poster, extrameta = info_tv(tmdbtitle)

           itemlist.append(
               Item(channel=__channel__,
                    thumbnail=poster,
                    fanart=fanart if fanart != "" else poster,
                    extrameta=extrameta,
                    plot=str(plot),
                    action="episodios" if item.extra == "serie" else "findvideos",
                    title=title,
                    url=scrapedurl,
                    fulltitle=title,
                    show=title,
                    folder=True))
        except:
           itemlist.append(
               Item(channel=__channel__,
                    action="episodios" if item.extra == "serie" else "findvideos",
                    title=title,
                    url=scrapedurl,
                    thumbnail=scrapedthumbnail,
                    fulltitle=title,
                    show=title,
                    plot=scrapedplot,
                    folder=True))

    ## Paginación
    next_page = scrapertools.find_single_match(data, 'rel="next" href="([^"]+)"')

    if next_page != "":
        itemlist.append(
                Item(channel=__channel__,
                     action="HomePage",
                     title="[COLOR yellow]Torna Home[/COLOR]",
                     folder=True)),
        itemlist.append(
                Item(channel=__channel__,
                     action="peliculas_tv",
                     title="[COLOR orange]Successivo >>[/COLOR]",
                     url=next_page,
                     thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png"))

    return itemlist


def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")


def categorias(item):
    logger.info("streamondemand.casacinema categorias")

    itemlist = []

    data = anti_cloudflare(item.url)

    # The categories are the options for the combo
    patron = '<td[^<]+<a href="([^"]+)">[^>]+>([^<]+)</a>[^/]+/td>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
                Item(channel=__channel__,
                     action="peliculas",
                     title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                     url=urlparse.urljoin(host, scrapedurl)))

    return itemlist

def info(title):
    logger.info("streamondemand.casacinema info")
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

def info_tv(title):
    logger.info("streamondemand.casacinema info")
    try:
        from core.tmdb import Tmdb
        oTmdb= Tmdb(texto_buscado=title, tipo= "tv", include_adult="false", idioma_busqueda="it")
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

def episodios(item):
    logger.info("anime sub ita - episodianime")

    itemlist = []

    # Downloads page
    data = anti_cloudflare(item.url)
    # Extracts the entries
    patron = '(.*?)<a href="(.*?)" target="_blank" rel="nofollow".*?>(.*?)</a>'
    matches = re.compile(patron).findall(data)

    for scrapedtitle, scrapedurl, scrapedserver in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedurl = scrapertools.decodeHtmlentities(scrapedurl)
        if scrapedtitle.startswith("<p>"):
            scrapedtitle = scrapedtitle[3:]

        itemlist.append(
            Item(channel=__channel__,
                 action="find_video_items",
                 title="[COLOR red]"+scrapedtitle+" [/COLOR]"+"[COLOR azure]"+item.fulltitle+" [/COLOR]"+"[COLOR orange] ["+scrapedserver+"][/COLOR]",
                 url=scrapedurl,
                 #data=scrapedurl,
                 thumbnail=item.thumbnail,
                 fulltitle=item.fulltitle,
                 show=item.show))

    return itemlist

def find_video_items(item=None, data=None, channel=""):
    logger.info("[launcher.py] findvideos")

    data=item.url

    # Descarga la página
    if data is None:
        from core import scrapertools
        data = scrapertools.cache_page(item.url)
        #logger.info(data)
    
    # Busca los enlaces a los videos
    from core.item import Item
    from servers import servertools
    listavideos = servertools.findvideos(data)

    if item is None:
        item = Item()

    itemlist = []
    for video in listavideos:
        scrapedtitle = item.title.strip() + " - " + video[0].strip()
        scrapedurl = video[1]
        server = video[2]
        
        itemlist.append( Item(channel=item.channel, title=item.title , action="play" , server=server, page=item.page, url=scrapedurl, thumbnail=item.thumbnail, show=item.show , plot=item.plot , folder=False) )

    return itemlist

def anti_cloudflare(url):
    # global headers

    try:
        resp_headers = scrapertools.get_headers_from_response(url, headers=headers)
        resp_headers = dict(resp_headers)
    except urllib2.HTTPError, e:
        resp_headers = e.headers

    if 'refresh' in resp_headers:
        time.sleep(int(resp_headers['refresh'][:1]))

        urlsplit = urlparse.urlsplit(url)
        h = urlsplit.netloc
        s = urlsplit.scheme
        scrapertools.get_headers_from_response(s + '://' + h + "/" + resp_headers['refresh'][7:], headers=headers)

    return scrapertools.cache_page(url, headers=headers)

