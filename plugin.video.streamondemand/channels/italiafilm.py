# -*- coding: iso-8859-1 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para italiafilm
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------
import re
import urlparse

from core import config
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "italiafilm"
__category__ = "F,S,A"
__type__ = "generic"
__title__ = "Italia-Film.co"
__language__ = "IT"

DEBUG = config.get_setting("debug")

host = "http://www.italia-film.co"

headers = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0'],
    ['Accept-Encoding', 'gzip, deflate']
]


def isGeneric():
    return True


def mainlist(item):
    logger.info("[italiafilm.py] mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film - Novita'[/COLOR]",
                     action="peliculas",
                     url="%s/category/film-streaming-2016-1/" % host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film HD[/COLOR]",
                     action="peliculas",
                     url="%s/category/film-hd/" % host,
                     thumbnail="http://i.imgur.com/3ED6lOP.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Anime e Cartoon[/COLOR]",
                     action="peliculas",
                     url="%s/category/anime-e-cartoon/" % host,
                     thumbnail="http://orig09.deviantart.net/df5a/f/2014/169/2/a/fist_of_the_north_star_folder_icon_by_minacsky_saya-d7mq8c8.png"),
                # Item(channel=__channel__,
                #      title="[COLOR azure]Contenuti per Genere[/COLOR]",
                #      action="categorias",
                #      url=host,
                #      thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/All%20Movies%20by%20Genre.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[/COLOR]",
                     action="peliculas_tv",
                     extra="serie",
                     url="%s/category/serie-tv/" % host,
                     thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/New%20TV%20Shows.png"),
                 Item(channel=__channel__,
                      title="[COLOR azure]Ultime serie TV[/COLOR]",
                      action="pel_tv",
                      extra="serie",
                      url="%s/ultimi-telefilm-streaming/" % host,
                      thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/All%20Movies%20by%20Genre.png"),
                      Item(channel=__channel__,
                      title="[COLOR azure]Ultimi anime inseriti[/COLOR]",
                      action="anime",
                      extra="serie",
                      url="%s/ultimi-telefilm-streaming/" % host,
                      thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/All%20Movies%20by%20Genre.png"),   
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Serie TV...[/COLOR]",
                     action="search",
                     extra="serie",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]
    return itemlist


def categorias(item):
    logger.info("[italiafilm.py] categorias")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    data = scrapertools.find_single_match(data, '<a href=".">Categorie</a>(.*?)</div>')

    patron = '<li[^>]+><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for url, title in matches:
        scrapedtitle = title
        scrapedurl = urlparse.urljoin(item.url, url)
        scrapedplot = ""
        scrapedthumbnail = ""
        if DEBUG: logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action='peliculas',
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))

    return itemlist


def search(item, texto):
    logger.info("[italiafilm.py] search " + texto)

    try:
        item.url = host + "/?s=" + texto
        if item.extra == "movie":
            return peliculas(item)
        if item.extra == "serie":
            return peliculas_tv(item)
    # Se captura la excepcion, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def peliculas(item):
    logger.info("[italiafilm.py] peliculas")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    patron = '<article(.*?)</article>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for match in matches:
        title = scrapertools.find_single_match(match, '<h3[^<]+<a href="[^"]+"[^<]+>([^<]+)</a>')
        title = title.replace("Streaming", "")
        title = scrapertools.decodeHtmlentities(title).strip()
        url = scrapertools.find_single_match(match, '<h3[^<]+<a href="([^"]+)"')
        plot = ""
        thumbnail = scrapertools.find_single_match(match, 'data-echo="([^"]+)"')

        if (DEBUG): logger.info("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action='episodios' if item.extra == 'serie' else 'findvideos',
                 fulltitle=title,
                 show=title,
                 title="[COLOR azure]" + title + "[/COLOR]",
                 url=url,
                 thumbnail=thumbnail,
                 plot=plot,
                 viewmode="movie_with_plot",
                 folder=True), tipo='movie'))

    # Siguiente
    try:
        pagina_siguiente = scrapertools.get_match(data, '<a class="next page-numbers" href="([^"]+)"')
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title="[COLOR yellow]Torna Home[/COLOR]",
                 folder=True)),
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 extra=item.extra,
                 title="[COLOR orange]Successivo >> [/COLOR]",
                 url=pagina_siguiente,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))
    except:
        pass

    return itemlist


def peliculas_tv(item):
    logger.info("[italiafilm.py] peliculas")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    patron = '<article(.*?)</article>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for match in matches:
        title = scrapertools.find_single_match(match, '<h3[^<]+<a href="[^"]+"[^<]+>([^<]+)</a>')
        title = title.replace("Streaming", "")
        title = scrapertools.decodeHtmlentities(title).strip()
        url = scrapertools.find_single_match(match, '<h3[^<]+<a href="([^"]+)"')
        plot = ""
        thumbnail = scrapertools.find_single_match(match, 'data-echo="([^"]+)"')

        if (DEBUG): logger.info("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action='episodios' if item.extra == 'serie' else 'findvideos',
                 fulltitle=title,
                 show=title,
                 title="[COLOR azure]" + title + "[/COLOR]",
                 url=url,
                 thumbnail=thumbnail,
                 plot=plot,
                 viewmode="movie_with_plot",
                 folder=True), tipo='tv'))

    # Siguiente
    try:
        pagina_siguiente = scrapertools.get_match(data, '<a class="next page-numbers" href="([^"]+)"')
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title="[COLOR yellow]Torna Home[/COLOR]",
                 folder=True)),
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_tv",
                 extra=item.extra,
                 title="[COLOR orange]Successivo >> [/COLOR]",
                 url=pagina_siguiente,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))
    except:
        pass

    return itemlist

def pel_tv(item):
    logger.info("[italiafilm.py] pel_tv")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    patron = '<li class="cat_7(.*?)</li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for match in matches:
        title = scrapertools.find_single_match(match, '<span class="tvseries_name">(.*?)</span>')
        t = scrapertools.find_single_match(match, '</i>(.*?)</a>')
        t = scrapertools.decodeHtmlentities(t).strip()
        title = title.replace("Streaming", "")
        title = scrapertools.decodeHtmlentities(title).strip()
        title = title + " - " + t
        url = scrapertools.find_single_match(match, '<a href="([^"]+)"')
        plot = ""
        thumbnail = scrapertools.find_single_match(match, 'data-echo="([^"]+)"')

        if (DEBUG): logger.info("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action='episodios' if item.extra == 'serie' else 'findvideos',
                 fulltitle=title,
                 show=title,
                 title="[COLOR azure]" + title + "[/COLOR]",
                 url=url,
                 thumbnail=thumbnail,
                 plot=plot,
                 viewmode="movie_with_plot",
                 folder=True), tipo='tv'))

    # Siguiente
    try:
        pagina_siguiente = scrapertools.get_match(data, '<a class="next page-numbers" href="([^"]+)"')
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title="[COLOR yellow]Torna Home[/COLOR]",
                 folder=True)),
        itemlist.append(
            Item(channel=__channel__,
                 action="pel_tv",
                 extra=item.extra,
                 title="[COLOR orange]Successivo >> [/COLOR]",
                 url=pagina_siguiente,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))
    except:
        pass

    return itemlist

def anime(item):
    logger.info("[italiafilm.py] anime")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    patron = '<li class="cat_19(.*?)</li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for match in matches:
        title = scrapertools.find_single_match(match, '<span class="tvseries_name">(.*?)</span>')
        t = scrapertools.find_single_match(match, '</i>(.*?)</a>')
        t = scrapertools.decodeHtmlentities(t).strip()
        title = title.replace("Streaming", "")
        title = scrapertools.decodeHtmlentities(title).strip()
        title = title + " - " + t
        url = scrapertools.find_single_match(match, '<a href="([^"]+)"')
        plot = ""
        thumbnail = scrapertools.find_single_match(match, 'data-echo="([^"]+)"')

        if (DEBUG): logger.info("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action='episodios' if item.extra == 'serie' else 'findvideos',
                 fulltitle=title,
                 show=title,
                 title="[COLOR azure]" + title + "[/COLOR]",
                 url=url,
                 thumbnail=thumbnail,
                 plot=plot,
                 viewmode="movie_with_plot",
                 folder=True), tipo='tv'))

    # Siguiente
    try:
        pagina_siguiente = scrapertools.get_match(data, '<a class="next page-numbers" href="([^"]+)"')
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title="[COLOR yellow]Torna Home[/COLOR]",
                 folder=True)),
        itemlist.append(
            Item(channel=__channel__,
                 action="anime",
                 extra=item.extra,
                 title="[COLOR orange]Successivo >> [/COLOR]",
                 url=pagina_siguiente,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))
    except:
        pass

    return itemlist

def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")


def episodios(item):
    def load_episodios(html, item, itemlist, lang_title):
        for data in scrapertools.decodeHtmlentities(html).splitlines():
            # Extrae las entradas
            end = data.find('<a ')
            if end > 0:
                scrapedtitle = re.sub(r'<[^>]*>', '', data[:end]).strip()
            else:
                scrapedtitle = ''
            if scrapedtitle == '':
                patron = '<a\s*href="[^"]+"\s*target="_blank">([^<]+)</a>'
                scrapedtitle = scrapertools.find_single_match(data, patron).strip()
            title = scrapertools.find_single_match(scrapedtitle, '\d+[^\d]+\d+')
            if title == '':
                title = scrapedtitle
            if title != '':
                itemlist.append(
                    Item(channel=__channel__,
                         action="findvid_serie",
                         title=title + " (" + lang_title + ")",
                         url=item.url,
                         thumbnail=item.thumbnail,
                         extra=data,
                         fulltitle=item.fulltitle,
                         show=item.show))

    logger.info("[italiafilm.py] episodios")

    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    start = data.find('id="pd_rating_holder')
    end = data.find('id="linkcorrotto-show"', start)

    data = data[start:end]

    lang_titles = []
    starts = []
    patron = r"STAGION[I|E](.*?ITA)?"
    matches = re.compile(patron, re.IGNORECASE).finditer(data)
    for match in matches:
        season_title = match.group()
        # if season_title != '':
        lang_titles.append('SUB ITA' if 'SUB' in season_title.upper() else 'ITA')
        starts.append(match.end())

    i = 1
    len_lang_titles = len(lang_titles)

    while i <= len_lang_titles:
        inizio = starts[i - 1]
        fine = starts[i] if i < len_lang_titles else -1

        html = data[inizio:fine]
        lang_title = lang_titles[i - 1]

        load_episodios(html, item, itemlist, lang_title)

        i += 1

    if len(itemlist) == 0:
        load_episodios(data, item, itemlist, 'ITA')

    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title=item.title,
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


def findvideos(item):
    logger.info("[italiafilm.py] findvideos")

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    itemlist = servertools.find_video_items(data=data)

    patron = '<iframe style="border: 0;" src="([^"]+)" width="[^"]*" height="[^"]*" scrolling="[^"]*" allowfullscreen="[^"]*"></iframe>'
    url = scrapertools.find_single_match(data, patron)
    if url:
        headers.append(['Referer', item.url])
        data = scrapertools.cache_page(url, headers=headers)
        html = []
        for num in scrapertools.find_multiple_matches(data, 'id="mlink_(\d+)"'):
            html.append(scrapertools.cache_page(url + '?host=%s' % num, headers=headers))

        itemlist.extend(servertools.find_video_items(data=''.join(html)))

    for videoitem in itemlist:
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist


def findvid_serie(item):
    logger.info("[italiafilm.py] findvideos")

    # Descarga la pagina
    data = item.extra

    html = [data]

    headers.append(['Referer', item.url])
    for url in scrapertools.find_multiple_matches(data, r'href="(http://hdlink\.[^?]+?)\?'):
        for num in scrapertools.find_multiple_matches(scrapertools.cache_page(url, headers=headers), 'id="mlink_(\d+)"'):
            html.append(scrapertools.cache_page(url + '?host=%s' % num, headers=headers))

    itemlist = servertools.find_video_items(data=''.join(html))
    for videoitem in itemlist:
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist
