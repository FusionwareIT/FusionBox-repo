# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para cineblog01
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

__channel__ = "cineblog01"
__category__ = "F,S,A"
__type__ = "generic"
__title__ = "CineBlog 01"
__language__ = "IT"

sito = "http://www.cb01.me"

headers = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', sito]
]

DEBUG = config.get_setting("debug")


def isGeneric():
    return True


def mainlist(item):
    logger.info("[cineblog01.py] mainlist")

    # Main options
    itemlist = [Item(channel=__channel__,
                     action="peliculas",
                     title="[COLOR azure]Cinema - Novita'[/COLOR]",
                     url=sito,
                     extra="movie",
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     action="peliculas",
                     title="[COLOR azure]Alta Definizione [HD][/COLOR]",
                     url="%s/tag/film-hd-altadefinizione/" % sito,
                     extra="movie",
                     thumbnail="http://jcrent.com/apple%20tv%20final/HD.png"),
                Item(channel=__channel__,
                     action="menuhd",
                     title="[COLOR azure]Menù HD[/COLOR]",
                     url=sito,
                     extra="movie",
                     thumbnail="http://files.softicons.com/download/computer-icons/disks-icons-by-wil-nichols/png/256x256/Blu-Ray.png"),
                Item(channel=__channel__,
                     action="menugeneros",
                     title="[COLOR azure]Per Genere[/COLOR]",
                     url=sito,
                     extra="movie",
                     thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/All%20Movies%20by%20Genre.png"),
                Item(channel=__channel__,
                     action="menuanyos",
                     title="[COLOR azure]Per Anno[/COLOR]",
                     url=sito,
                     extra="movie",
                     thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/Movie%20Year.png"),
                Item(channel=__channel__,
                     action="search",
                     title="[COLOR yellow]Cerca Film[/COLOR]",
                     extra="movie",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"),
                Item(channel=__channel__,
                     action="listserie",
                     title="[COLOR azure]Serie Tv - Novita'[/COLOR]",
                     url="%s/serietv/" % sito,
                     extra="serie",
                     thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/New%20TV%20Shows.png"),
                Item(channel=__channel__,
                     action="search",
                     title="[COLOR yellow]Cerca Serie Tv[/COLOR]",
                     extra="serie",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist


def peliculas(item):
    logger.info("[cineblog01.py] mainlist")
    itemlist = []

    if item.url == "":
        item.url = sito

    # Descarga la página
    data = scrapertools.anti_cloudflare(item.url, headers)

    # Extrae las entradas (carpetas)
    patronvideos = '<div class="span4".*?<a.*?<p><img src="([^"]+)".*?'
    patronvideos += '<div class="span8">.*?<a href="([^"]+)"> <h1>([^"]+)</h1></a>.*?'
    patronvideos += '<strong>([^<]*)</strong>.*?<br />([^<+]+)'
    matches = re.compile(patronvideos, re.DOTALL).finditer(data)

    for match in matches:
        scrapedtitle = scrapertools.unescape(match.group(3))
        scrapedurl = urlparse.urljoin(item.url, match.group(2))
        scrapedthumbnail = urlparse.urljoin(item.url, match.group(1))
        scrapedthumbnail = scrapedthumbnail.replace(" ", "%20")
        scrapedplot = scrapertools.unescape("[COLOR orange]" + match.group(4) + "[/COLOR]\n" + match.group(5).strip())
        scrapedplot = scrapertools.htmlclean(scrapedplot).strip()
        if DEBUG: logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 viewmode="movie_with_plot"), tipo='movie'))

    # Next page mark
    try:
        bloque = scrapertools.get_match(data, "<div id='wp_page_numbers'>(.*?)</div>")
        patronvideos = '<a href="([^"]+)">></a></li>'
        matches = re.compile(patronvideos, re.DOTALL).findall(bloque)
        scrapertools.printMatches(matches)

        if len(matches) > 0:
            scrapedtitle = "[COLOR orange]Successivo>>[/COLOR]"
            scrapedurl = matches[0]
            scrapedthumbnail = ""
            scrapedplot = ""
            if (DEBUG): logger.info(
                "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
            itemlist.append(
                Item(channel=__channel__,
                     action="HomePage",
                     title="[COLOR yellow]Torna Home[/COLOR]",
                     folder=True)),
            itemlist.append(
                Item(channel=__channel__,
                     action="peliculas",
                     title=scrapedtitle,
                     url=scrapedurl,
                     thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                     extra=item.extra,
                     plot=scrapedplot))
    except:
        pass

    return itemlist


def menugeneros(item):
    logger.info("[cineblog01.py] menugeneros")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, '<select name="select2"(.*?)</select>')

    # The categories are the options for the combo  
    patron = '<option value="([^"]+)">([^<]+)</option>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url, titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url, url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 extra=item.extra,
                 plot=scrapedplot))

    return itemlist


def menuhd(item):
    logger.info("[cineblog01.py] menugeneros")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, '<select name="select1"(.*?)</select>')

    # The categories are the options for the combo  
    patron = '<option value="([^"]+)">([^<]+)</option>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url, titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url, url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 extra=item.extra,
                 plot=scrapedplot))

    return itemlist


def menuanyos(item):
    logger.info("[cineblog01.py] menuvk")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, '<select name="select3"(.*?)</select>')

    # The categories are the options for the combo  
    patron = '<option value="([^"]+)">([^<]+)</option>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url, titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url, url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 extra=item.extra,
                 plot=scrapedplot))

    return itemlist


# Al llamarse "search" la función, el launcher pide un texto a buscar y lo añade como parámetro
def search(item, texto):
    logger.info("[cineblog01.py] " + item.url + " search " + texto)

    try:

        if item.extra == "movie":
            item.url = "http://www.cb01.me/?s=" + texto
            return peliculas(item)
        if item.extra == "serie":
            item.url = "http://www.cb01.me/serietv/?s=" + texto
            return listserie(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def listserie(item):
    logger.info("[cineblog01.py] mainlist")
    itemlist = []

    # Descarga la página
    data = scrapertools.anti_cloudflare(item.url, headers)

    # Extrae las entradas (carpetas)
    patronvideos = '<div class="span4">\s*<a href="([^"]+)"><img src="([^"]+)".*?<div class="span8">.*?<h1>([^<]+)</h1></a>(.*?)<br><a'
    matches = re.compile(patronvideos, re.DOTALL).finditer(data)

    for match in matches:
        scrapedtitle = scrapertools.unescape(match.group(3))
        scrapedurl = match.group(1)
        scrapedthumbnail = match.group(2)
        scrapedplot = scrapertools.unescape(match.group(4))
        scrapedplot = scrapertools.htmlclean(scrapedplot).strip()
        if (DEBUG): logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 extra=item.extra,
                 plot=scrapedplot), tipo='tv'))

    # Put the next page mark
    try:
        next_page = scrapertools.get_match(data, "<link rel='next' href='([^']+)'")
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title="[COLOR yellow]Torna Home[/COLOR]",
                 folder=True)),
        itemlist.append(
            Item(channel=__channel__,
                 action="listserie",
                 title="[COLOR orange]Successivo>>[/COLOR]",
                 url=next_page,
                 extra=item.extra,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png", ))
    except:
        pass

    return itemlist


def listaaz(item):
    logger.info("[cineblog01.py] listaaz")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers)

    # Narrow search by selecting only the combo
    patron = '<a href="#char_5a" title="Go to the letter Z">Z</a></span></div>(.*?)</ul></div><div style="clear:both;"></div></div>'
    bloque = scrapertools.get_match(data, patron)

    # The categories are the options for the combo
    patron = '<li><a href="([^"]+)"><span class="head">([^<]+)</span></a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url, titulo in matches:
        scrapedtitle = titulo
        scrapedurl = url
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=[" + scrapedtitle + "], url=[" + scrapedurl + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="episodios",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail="http://www.justforpastime.net/uploads/3/8/1/5/38155083/273372_orig.jpg",
                 extra=item.extra,
                 plot=scrapedplot))

    return itemlist


def episodios(item):
    itemlist = []

    if item.extra == 'serie':
        itemlist.extend(episodios_serie(item))

    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title=item.title,
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodios" + "###" + item.extra,
                 show=item.show))
        itemlist.append(
            Item(channel=item.channel,
                 title="Scarica tutti gli episodi della serie",
                 url=item.url,
                 action="download_all_episodes",
                 extra="episodios" + "###" + item.extra,
                 show=item.show))

    return itemlist


def episodios_serie(item):
    def load_episodios(html, item, itemlist, lang_title):
        for data in scrapertools.decodeHtmlentities(html).splitlines():
            ## Extrae las entradas
            end = data.find('<a ')
            if end > 0:
                scrapedtitle = re.sub(r'<[^>]*>', '', data[:end]).strip()
            else:
                scrapedtitle = ''
            if scrapedtitle == '':
                patron = '<a\s*href="[^"]+"\s*target="_blank">([^<]+)</a>'
                scrapedtitle = scrapertools.find_single_match(data, patron).strip()
            title = scrapertools.find_single_match(scrapedtitle, '\d+[^\d]+?\d+')
            if title == '':
                title = scrapedtitle
            if title != '':
                itemlist.append(
                    Item(channel=__channel__,
                         action="findvideos",
                         title=title + " (" + lang_title + ")",
                         url=data,
                         thumbnail=item.thumbnail,
                         extra=item.extra,
                         fulltitle=item.show + ' | ' + title + " (" + lang_title + ")",
                         show=item.show))

    logger.info("[cineblog01.py] episodios")

    itemlist = []

    # Descarga la página
    data = scrapertools.anti_cloudflare(item.url, headers)

    start = data.find('<td bgcolor="#ECEAE1">')
    end = data.find('</td>', start)

    data = data[start:end]

    lang_titles = []
    starts = []
    patron = r"STAGION[I|E].*?ITA"
    matches = re.compile(patron).finditer(data)
    for match in matches:
        season_title = match.group()
        if season_title != '':
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
        patron = r'<div class="sp-head(?: unfolded)?" title="Expand">([^<]+)</div>\s*<div class="sp-body(?: folded)?">(.*?)<div class="spdiv">\[chiudi\]</div>'
        matches = re.compile(patron, re.DOTALL).findall(data)
        for lang_title, match in matches:
            lang_title = 'SUB ITA' if 'SUB' in lang_title.upper() else 'ITA'
            load_episodios(match, item, itemlist, lang_title)

        if len(itemlist) == 0:
            patron = '<strong>([^<]+)</strong></p>\s*(?:<p>&nbsp;</p>\s*)+(.*?)<p>&nbsp;</p>'
            matches = re.compile(patron, re.DOTALL).findall(data)
            for lang_title, match in matches:
                lang_title = 'SUB ITA' if 'SUB' in lang_title.upper() else 'ITA'
                load_episodios(match, item, itemlist, lang_title)

    return itemlist


def findvideos(item):
    if item.extra == "movie":
        return findvid_film(item)
    if item.extra == 'serie':
        return findvid_serie(item)


def findvid_film(item):
    logger.info("[cineblog01.py] findvideos")

    itemlist = []

    # Descarga la página
    data = scrapertools.anti_cloudflare(item.url, headers)
    data = scrapertools.decodeHtmlentities(data).replace('http://cineblog01.pw', 'http://k4pp4.pw')

    # Extract the quality format
    patronvideos = '>([^<]+)</strong></div>'
    matches = re.compile(patronvideos, re.DOTALL).finditer(data)
    QualityStr = ""
    for match in matches:
        QualityStr = scrapertools.unescape(match.group(1))[6:]

    # Extrae las entradas
    streaming = scrapertools.find_single_match(data, '<strong>Streaming:</strong>(.*?)<table height="30">')
    patron = '<td><a href="([^"]+)" target="_blank">([^<]+)</a></td>'
    matches = re.compile(patron, re.DOTALL).findall(streaming)
    for scrapedurl, scrapedtitle in matches:
        print "##### findvideos Streaming ## %s ## %s ##" % (scrapedurl, scrapedtitle)
        title = "[COLOR orange]Streaming:[/COLOR] " + item.title + " [COLOR grey]" + QualityStr + "[/COLOR] [COLOR blue][" + scrapedtitle + "][/COLOR]"
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 title=title,
                 url=scrapedurl,
                 fulltitle=item.fulltitle,
                 thumbnail=item.thumbnail,
                 show=item.show,
                 folder=False))

    streaming_hd = scrapertools.find_single_match(data, '<strong>Streaming HD[^<]+</strong>(.*?)<table height="30">')
    patron = '<td><a href="([^"]+)" target="_blank">([^<]+)</a></td>'
    matches = re.compile(patron, re.DOTALL).findall(streaming_hd)
    for scrapedurl, scrapedtitle in matches:
        print "##### findvideos Streaming HD ## %s ## %s ##" % (scrapedurl, scrapedtitle)
        title = "[COLOR yellow]Streaming HD:[/COLOR] " + item.title + " [COLOR grey]" + QualityStr + "[/COLOR] [COLOR blue][" + scrapedtitle + "][/COLOR]"
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 title=title,
                 url=scrapedurl,
                 fulltitle=item.fulltitle,
                 thumbnail=item.thumbnail,
                 show=item.show,
                 folder=False))

    streaming_3D = scrapertools.find_single_match(data, '<strong>Streaming 3D[^<]+</strong>(.*?)<table height="30">')
    patron = '<td><a href="([^"]+)" target="_blank">([^<]+)</a></td>'
    matches = re.compile(patron, re.DOTALL).findall(streaming_3D)
    for scrapedurl, scrapedtitle in matches:
        print "##### findvideos Streaming 3D ## %s ## %s ##" % (scrapedurl, scrapedtitle)
        title = "[COLOR pink]Streaming 3D:[/COLOR] " + item.title + " [COLOR grey]" + QualityStr + "[/COLOR] [COLOR blue][" + scrapedtitle + "][/COLOR]"
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 title=title,
                 url=scrapedurl,
                 fulltitle=item.fulltitle,
                 thumbnail=item.thumbnail,
                 show=item.show,
                 folder=False))

    download = scrapertools.find_single_match(data, '<strong>Download:</strong>(.*?)<table height="30">')
    patron = '<td><a href="([^"]+)" target="_blank">([^<]+)</a></td>'
    matches = re.compile(patron, re.DOTALL).findall(download)
    for scrapedurl, scrapedtitle in matches:
        print "##### findvideos Download ## %s ## %s ##" % (scrapedurl, scrapedtitle)
        title = "[COLOR aqua]Download:[/COLOR] " + item.title + " [COLOR grey]" + QualityStr + "[/COLOR] [COLOR blue][" + scrapedtitle + "][/COLOR]"
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 title=title,
                 url=scrapedurl,
                 fulltitle=item.fulltitle,
                 thumbnail=item.thumbnail,
                 show=item.show,
                 folder=False))

    download_hd = scrapertools.find_single_match(data,
                                                 '<strong>Download HD[^<]+</strong>(.*?)<table width="100%" height="20">')
    patron = '<td><a href="([^"]+)" target="_blank">([^<]+)</a></td>'
    matches = re.compile(patron, re.DOTALL).findall(download_hd)
    for scrapedurl, scrapedtitle in matches:
        print "##### findvideos Download HD ## %s ## %s ##" % (scrapedurl, scrapedtitle)
        title = "[COLOR azure]Download HD:[/COLOR] " + item.title + " [COLOR grey]" + QualityStr + "[/COLOR] [COLOR blue][" + scrapedtitle + "][/COLOR]"
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 title=title,
                 url=scrapedurl,
                 fulltitle=item.fulltitle,
                 thumbnail=item.thumbnail,
                 show=item.show,
                 folder=False))

    if len(itemlist) == 0:
        itemlist = servertools.find_video_items(item=item)

    return itemlist


def findvid_serie(item):
    logger.info("[cineblog01.py] findvideos")

    itemlist = []

    # Descarga la página
    data = item.url
    data = data.replace('http://cineblog01.pw', 'http://k4pp4.pw')

    patron = '<a\s*href="([^"]+)"\s*target="_blank">([^<]+)</a>'
    # Extrae las entradas
    matches = re.compile(patron, re.DOTALL).finditer(data)
    for match in matches:
        scrapedurl = match.group(1)
        scrapedtitle = match.group(2)
        title = item.title + " [COLOR blue][" + scrapedtitle + "][/COLOR]"
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 title=title,
                 url=scrapedurl,
                 fulltitle=item.fulltitle,
                 show=item.show,
                 folder=False))

    return itemlist


def play(item):
    logger.info("[cineblog01.py] play")

    print "##############################################################"
    if "go.php" in item.url:
        data = scrapertools.anti_cloudflare(item.url, headers)
        try:
            data = scrapertools.get_match(data, 'window.location.href = "([^"]+)";')
        except IndexError:
            #            data = scrapertools.get_match(data, r'<a href="([^"]+)">clicca qui</a>')
            #   In alternativa, dato che a volte compare "Clicca qui per proseguire":
            data = scrapertools.get_match(data, r'<a href="([^"]+)".*?class="btn-wrapper">.*?licca.*?</a>')
        if 'vcrypt' in data:
            data = scrapertools.get_header_from_response(data, headers=headers, header_to_get="Location")
        print "##### play go.php data ##\n%s\n##" % data
    elif "/link/" in item.url:
        data = scrapertools.anti_cloudflare(item.url, headers)
        from core import jsunpack

        try:
            data = scrapertools.get_match(data, "(eval\(function\(p,a,c,k,e,d.*?)</script>")
            # data = scrapertools.get_match(data, "(eval.function.p,a,c,k,e,.*?)</script>")
            data = jsunpack.unpack(data)
            print "##### play /link/ unpack ##\n%s\n##" % data
        except IndexError:
            print "##### The content is yet unpacked"

        data = scrapertools.get_match(data, 'var link(?:\s)?=(?:\s)?"([^"]+)";')
        print "##### play /link/ data ##\n%s\n##" % data
    else:
        data = item.url
        print "##### play else data ##\n%s\n##" % data
    print "##############################################################"

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = item.show
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist


def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")
