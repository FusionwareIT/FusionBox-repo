# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand 5
# Copyright 2015 tvalacarta@gmail.com
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
# ------------------------------------------------------------
# This file is part of streamondemand 5.
#
# streamondemand 5 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# streamondemand 5 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with streamondemand 5.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------------------
# Search trailers from youtube, filmaffinity, abandomoviez, vimeo, etc...
# --------------------------------------------------------------------------------

import re
import urllib
import urlparse

from core import config
from core import jsontools
from core import logger
from core import scrapertools
from core import servertools
from platformcode import platformtools

DEBUG = config.get_setting("debug")
# Para habilitar o no la opción de búsqueda manual
if config.is_xbmc() or config.get_platform() == "mediaserver":
    keyboard = True
else:
    keyboard = False


def buscartrailer(item):
    logger.info("streamondemand.channels.trailertools buscartrailer")

    # Se elimina la opciçon de Buscar Trailer del menú contextual para evitar redundancias
    item.context = item.context.replace("5", "")
    item.text_color = ""
    # Si no se indica el parámetro contextual se entiende que no se ejecuta desde este mení
    if item.contextual == "":
        item.contextual = False

    itemlist = []
    if item.contentTitle != "":
        item.contentTitle = item.contentTitle.strip()
    elif keyboard:
        item.contentTitle = platformtools.dialog_input(heading="Introduce el título a buscar")
        if item.contentTitle is None:
            item.contentTitle = item.fulltitle.strip()
        else:
            item.contentTitle = item.contentTitle.strip()
    else:
        item.contentTitle = item.fulltitle.strip()
        
    item.year = item.infoLabels['year'] if "year" in item.infoLabels else ""
    logger.info("streamondemand.channels.trailertools Búsqueda: %s" % item.contentTitle)
    logger.info("streamondemand.channels.trailertools Año: %s" % item.year)

    # Lista de acciones si se ejecuta desde el menú contextual
    if item.action == "manual_search":
        itemlist = manual_search(item)
        item.contentTitle = itemlist[0].contentTitle
    elif item.action == "youtube_search":
        itemlist = youtube_search(item)
    elif item.action == "filmaffinity_search":
        itemlist = filmaffinity_search(item)
    elif item.action == "abandomoviez_search":
        itemlist = abandomoviez_search(item)
    elif item.action == "jayhap_search":
        itemlist = jayhap_search(item)
    else:
        if "trailer" in item.infoLabels and item.infoLabels['trailer'] != "":
            url = item.infoLabels['trailer']
            if "youtube" in url:
                url = url.replace("embed/", "watch?v=")
            titulo, url, server = servertools.findvideos(url)[0]
            title = "Trailer por defecto  [" + server + "]"
            itemlist.append(item.clone(title=title, url=url, server=server, action="play"))
        if item.show != "" or ("tvshowtitle" in item.infoLabels and item.infoLabels['tvshowtitle'] != ""):
            type = "tv"
        else:
            type = "movie"
        try:
            itemlist.extend(tmdb_trailers(item, type))
        except:
            import traceback
            logger.error(traceback.format_exc())
        
        title = "[COLOR green]%s[/COLOR]" if item.contextual else "%s"
        itemlist.append(item.clone(title=title % "Búsqueda en Youtube", action="youtube_search",
                                   text_color="green"))
        itemlist.append(item.clone(title=title % "Búsqueda en Filmaffinity",
                                   action="filmaffinity_search", text_color="green"))
        # Si se trata de una serie, no se incluye la opción de buscar en Abandomoviez
        if item.show == "" and ("tvshowtitle" not in item.infoLabels or item.infoLabels['tvshowtitle'] == ""):
            itemlist.append(item.clone(title=title % "Búsqueda en Abandomoviez",
                                       action="abandomoviez_search", text_color="green"))
        itemlist.append(item.clone(title=title % "Búsqueda en Jayhap (Youtube, Vimeo & Dailymotion)",
                                   action="jayhap_search", text_color="green"))

    if item.contextual:
        opciones = []
        if itemlist:
            for video_url in itemlist:
                opciones.append(video_url.title)

            seleccion = platformtools.dialog_select("Buscando: "+item.contentTitle, opciones)
            logger.info("seleccion=%d" % seleccion)
            logger.info("seleccion=%s" % opciones[seleccion])

            if seleccion < 0:
                return
            else:
                item = itemlist[seleccion]
                if "search" in item.action:
                    buscartrailer(item)
                else:
                    if item.action == "play":
                        from platformcode import xbmctools
                        xbmctools.play_video(item)
                    return
    else:
        return itemlist


def manual_search(item):
    logger.info("streamondemand.channels.trailertools manual_search")
    texto = platformtools.dialog_input(default=item.contentTitle, heading=config.get_localized_string(30112))
    if texto is not None:
        if item.extra == "abandomoviez":
            return abandomoviez_search(item.clone(contentTitle=texto, page="", year=""))
        elif item.extra == "youtube":
            return youtube_search(item.clone(contentTitle=texto, page=""))
        elif item.extra == "filmaffinity":
            return filmaffinity_search(item.clone(contentTitle=texto, page="", year=""))
        elif item.extra == "jayhap":
            return jayhap_search(item.clone(contentTitle=texto))


def tmdb_trailers(item, type="movie"):
    logger.info("streamondemand.channels.trailertools tmdb_trailers")

    from core.tmdb import Tmdb
    itemlist = []
    tmdb_search = None
    if "tmdb_id" in item.infoLabels and item.infoLabels['tmdb_id'] != "":
        tmdb_search = Tmdb(id_Tmdb=item.infoLabels['tmdb_id'], tipo=type, idioma_busqueda='it')
    elif "year" in item.infoLabels and item.infoLabels['year'] != "":
        tmdb_search = Tmdb(texto_buscado=item.contentTitle, tipo=type, year=item.infoLabels['year'])

    if tmdb_search:
        for result in tmdb_search.get_videos():
            title = result['name'] + " [" + result['size'] + "p] (" + result['language'].replace("en", "ING")\
                    .replace("es", "ESP")+")  [tmdb/youtube]"
            itemlist.append(item.clone(action="play", title=title, url=result['url'], server="youtube"))
    
    return itemlist


def youtube_search(item):
    logger.info("streamondemand.channels.trailertools youtube_search")
    itemlist = []

    if item.extra != "youtube":
        item.contentTitle += " trailer"
    # Comprueba si es una búsqueda de cero o viene de la opción Siguiente
    if item.page != "":
        data = scrapertools.downloadpage(item.page)
    else:
        titulo = urllib.quote(item.contentTitle)
        titulo = titulo.replace("%20", "+")
        data = scrapertools.downloadpage("https://www.youtube.com/results?sp=EgIQAQ%253D%253D&q="+titulo)

    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    patron = '<span class="yt-thumb-simple">.*?(?:src="https://i.ytimg.com/|data-thumb="https://i.ytimg.com/)([^"]+)"' \
             '.*?<h3 class="yt-lockup-title ">.*?<a href="([^"]+)".*?title="([^"]+)".*?' \
             '</a><span class="accessible-description".*?>.*?(\d+:\d+)'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedthumbnail, scrapedurl, scrapedtitle, scrapedduration in matches:
        scrapedthumbnail = urlparse.urljoin("https://i.ytimg.com/", scrapedthumbnail)
        scrapedtitle = scrapedtitle.decode("utf-8")
        scrapedtitle = scrapedtitle + " (" + scrapedduration + ")"
        if item.contextual:
            scrapedtitle = "[COLOR white]%s[/COLOR]" % scrapedtitle
        url = urlparse.urljoin('https://www.youtube.com/', scrapedurl)
        itemlist.append(item.clone(title=scrapedtitle, action="play", server="youtube", url=url,
                                   thumbnail=scrapedthumbnail, text_color="white"))
    
    next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"[^>]+><span class="yt-uix-button-content">'
                                                     'Siguiente')
    if next_page != "":
        next_page = urlparse.urljoin("https://www.youtube.com", next_page)
        itemlist.append(item.clone(title=">> Siguiente", action="youtube_search", extra="youtube", page=next_page,
                                   thumbnail="", text_color=""))
    
    if not itemlist:
        itemlist.append(item.clone(title="La búsqueda no ha dado resultados (%s)" % item.contentTitle,
                                   action="", thumbnail="", text_color=""))

    if keyboard:
        title = "[COLOR green]%s[/COLOR]" if item.contextual else "%s"
        itemlist.append(item.clone(title=title % "Búsqueda Manual en Youtube", action="manual_search",
                                   text_color="green", thumbnail="", extra="youtube"))

    return itemlist


def abandomoviez_search(item):
    logger.info("streamondemand.channels.trailertools abandomoviez_search")

    # Comprueba si es una búsqueda de cero o viene de la opción Siguiente
    if item.page != "":
        data = scrapertools.downloadpage(item.page)
    else:
        titulo = item.contentTitle.decode('utf-8').encode('iso-8859-1')
        post = urllib.urlencode({'query': titulo, 'searchby': '1', 'posicion': '1', 'orden': '1',
                                 'anioin': item.year, 'anioout': item.year, 'orderby': '1'})
        url = "http://www.abandomoviez.net/db/busca_titulo_advance.php"
        item.prefix = "db/"
        data = scrapertools.downloadpage(url, post=post)
        if "No hemos encontrado ninguna" in data:
            url = "http://www.abandomoviez.net/indie/busca_titulo_advance.php"
            item.prefix = "indie/"
            data = scrapertools.downloadpage(url, post=post).decode("iso-8859-1").encode('utf-8')
            logger.info(data)

    itemlist = []
    devuelve = []
    patron = '(?:<td width="85"|<div class="col-md-2 col-sm-2 col-xs-3">).*?<img src="([^"]+)"' \
             '.*?href="([^"]+)">(.*?)(?:<\/td>|<\/small>)'
    matches = scrapertools.find_multiple_matches(data, patron)
    # Si solo hay un resultado busca directamente los trailers, sino lista todos los resultados
    if len(matches) == 1:
        item.url = urlparse.urljoin("http://www.abandomoviez.net/%s" % item.prefix, matches[0][1])
        item.thumbnail = matches[0][0]
        devuelve = search_links_abando(item)
    elif len(matches) > 1:
        for scrapedthumbnail, scrapedurl, scrapedtitle in matches:
            scrapedurl = urlparse.urljoin("http://www.abandomoviez.net/%s" % item.prefix, scrapedurl)
            scrapedtitle = scrapertools.htmlclean(scrapedtitle)
            itemlist.append(item.clone(title=scrapedtitle, action="search_links_abando",
                                       url=scrapedurl, thumbnail=scrapedthumbnail, text_color="white"))

        next_page = scrapertools.find_single_match(data, '<a href="([^"]+)">Siguiente')
        if next_page != "":
            next_page = urlparse.urljoin("http://www.abandomoviez.net/%s" % item.prefix, next_page)
            itemlist.append(item.clone(title=">> Siguiente", action="abandomoviez_search", page=next_page, thumbnail="",
                                       text_color=""))

        if item.contextual:
            opciones = []
            for item_abando in itemlist:
                opciones.append(item_abando.title)

            seleccion = platformtools.dialog_select("Buscando: "+item.contentTitle, opciones)
            logger.info("seleccion=%d" % seleccion)
            logger.info("seleccion=%s" % opciones[seleccion])
            if seleccion < 0:
                return
            else:
                item_abando = itemlist[seleccion]
                if item_abando.title == ">> Siguiente":
                    return buscartrailer(item_abando)
                else:
                    devuelve = search_links_abando(item_abando)
        else:
            devuelve = itemlist

    if not devuelve:
        devuelve.append(item.clone(title="La búsqueda no ha dado resultados", action="", thumbnail="",
                                   text_color=""))
    
        if keyboard:
            title = "[COLOR green]%s[/COLOR]" if item.contextual else "%s"
            devuelve.append(item.clone(title=title % "Búsqueda Manual en Abandomoviez",
                                       action="manual_search", thumbnail="", text_color="green", extra="abandomoviez"))

    return devuelve


def search_links_abando(item):
    logger.info("streamondemand.channels.trailertools search_links_abando")

    data = scrapertools.downloadpage(item.url)
    itemlist = []
    if "Lo sentimos, no tenemos trailer" in data:
        itemlist.append(item.clone(title="No hay ningún vídeo disponible", action="", text_color=""))
    else:
        if item.contextual:
            progreso = platformtools.dialog_progress("Buscando en abandomoviez", "Cargando trailers...")
            progreso.update(10)
            i = 0
            message = "Cargando trailers..."
        patron = '<div class="col-md-3 col-xs-6"><a href="([^"]+)".*?' \
                 'Images/(\d+).gif.*?</div><small>(.*?)</small>'
        matches = scrapertools.find_multiple_matches(data, patron)
        if len(matches) == 0:
            trailer_url = scrapertools.find_single_match(data, '<iframe.*?src="([^"]+)"')
            if trailer_url != "":
                trailer_url = trailer_url.replace("embed/", "watch?v=")
                itemlist.append(item.clone(title="Trailer  [youtube]", url=trailer_url, server="youtube",
                                           action="play", text_color="white"))
        else:
            for scrapedurl, language, scrapedtitle in matches:
                idioma = " (ESP)" if language == "1" else " (V.O)"
                scrapedurl = urlparse.urljoin("http://www.abandomoviez.net/%s" % item.prefix, scrapedurl)
                scrapedtitle = scrapertools.htmlclean(scrapedtitle) + idioma + "  [youtube]"
                if item.contextual:
                    i += 1
                    message += ".."
                    progreso.update(10 + (90*i/len(matches)), message)
                    scrapedtitle = "[COLOR white]%s[/COLOR]" % scrapedtitle

                data_trailer = scrapertools.downloadpage(scrapedurl)
                trailer_url = scrapertools.find_single_match(data_trailer, 'iframe.*?src="([^"]+)"')
                trailer_url = trailer_url.replace("embed/", "watch?v=")
                itemlist.append(item.clone(title=scrapedtitle, url=trailer_url, server="youtube",
                                           action="play", text_color="white"))
        
        if item.contextual:
            progreso.close()

    if keyboard:
        title = "[COLOR green]%s[/COLOR]" if item.contextual else "%s"
        itemlist.append(item.clone(title=title % "Búsqueda Manual en Abandomoviez",
                                   action="manual_search", thumbnail="", text_color="green", extra="abandomoviez"))
    return itemlist


def filmaffinity_search(item):
    logger.info("streamondemand.channels.trailertools filmaffinity_search")

    # Comprueba si es una búsqueda de cero o viene de la opción Siguiente
    if item.page != "":
        data = scrapertools.downloadpage(item.page)
    else:
        params = urllib.urlencode([('stext', item.contentTitle), ('stype%5B%5D', 'title'), ('country', ''),
                                   ('genre', ''), ('fromyear', item.year), ('toyear', item.year)])
        url = "http://www.filmaffinity.com/es/advsearch.php?%s" % params
        data = scrapertools.downloadpage(url)

    devuelve = []
    itemlist = []
    patron = '<div class="mc-poster">.*?<img.*?src="([^"]+)".*?' \
             '<div class="mc-title"><a  href="/es/film(\d+).html"[^>]+>(.*?)<img'
    matches = scrapertools.find_multiple_matches(data, patron)
    # Si solo hay un resultado, busca directamente los trailers, sino lista todos los resultados
    if len(matches) == 1:
        item.url = "http://www.filmaffinity.com/es/evideos.php?movie_id=%s" % matches[0][1]
        item.thumbnail = matches[0][0]
        if not item.thumbnail.startswith("http"):
            item.thumbnail = "http://www.filmaffinity.com" + item.thumbnail
        devuelve = search_links_filmaff(item)
    elif len(matches) > 1:
        for scrapedthumbnail, id, scrapedtitle in matches:
            if not scrapedthumbnail.startswith("http"):
                scrapedthumbnail = "http://www.filmaffinity.com" + scrapedthumbnail
            scrapedurl = "http://www.filmaffinity.com/es/evideos.php?movie_id=%s" % id
            scrapedtitle = unicode(scrapedtitle, encoding="utf-8", errors="ignore")
            scrapedtitle = scrapertools.htmlclean(scrapedtitle)
            itemlist.append(item.clone(title=scrapedtitle, url=scrapedurl,
                                       action="search_links_filmaff", thumbnail=scrapedthumbnail, text_color="white"))

        next_page = scrapertools.find_single_match(data, '<a href="([^"]+)">&gt;&gt;</a>')
        if next_page != "":
            next_page = urlparse.urljoin("http://www.filmaffinity.com/es/", next_page)
            itemlist.append(item.clone(title=">> Siguiente", page=next_page, action="filmaffinity_search", thumbnail="",
                                       text_color=""))

        if item.contextual:
            opciones = []
            for item_film in itemlist:
                opciones.append(item_film.title)
            seleccion = platformtools.dialog_select("Buscando: "+item.contentTitle, opciones)
            logger.info("seleccion=%d" % seleccion)
            logger.info("seleccion=%s" % opciones[seleccion])
            if seleccion < 0:
                return
            else:
                item_film = itemlist[seleccion]
                if item_film.title == ">> Siguiente":
                    return buscartrailer(item_film)
                else:
                    devuelve = search_links_filmaff(item_film)
        else:
            devuelve = itemlist

    if not devuelve:
        devuelve.append(item.clone(title="La búsqueda no ha dado resultados (%s)" % item.contentTitle,
                                   action="", thumbnail="", text_color=""))

        if keyboard:
            title = "[COLOR green]%s[/COLOR]" if item.contextual else "%s"
            devuelve.append(item.clone(title=title % "Búsqueda Manual en Filmaffinity",
                                       action="manual_search", text_color="green", thumbnail="", extra="filmaffinity"))
        
    return devuelve


def search_links_filmaff(item):
    logger.info("streamondemand.channels.trailertools search_links_filmaff")
    
    itemlist = []
    data = scrapertools.downloadpage(item.url)
    if not "iframe" in data:
        itemlist.append(item.clone(title="No hay ningún vídeo disponible", action="", text_color=""))
    else:
        patron = '<a class="lnkvvid".*?<b>(.*?)</b>.*?iframe.*?src="([^"]+)"'
        matches = scrapertools.find_multiple_matches(data, patron)
        for scrapedtitle, scrapedurl in matches:
            trailer_url = urlparse.urljoin("http:", scrapedurl).replace("embed/", "watch?v=")
            server = servertools.get_server_from_url(trailer_url)
            scrapedtitle = unicode(scrapedtitle, encoding="utf-8", errors="ignore")
            scrapedtitle = scrapertools.htmlclean(scrapedtitle)
            scrapedtitle += "  [" + server + "]"
            if item.contextual:
                scrapedtitle = "[COLOR white]%s[/COLOR]" % scrapedtitle            
            itemlist.append(item.clone(title=scrapedtitle, url=trailer_url, server=server,
                                       action="play", text_color="white"))

    if keyboard:
        title = "[COLOR green]%s[/COLOR]" if item.contextual else "%s"
        itemlist.append(item.clone(title=title % "Búsqueda Manual en Filmaffinity",
                                   action="manual_search", thumbnail="", text_color="green", extra="filmaffinity"))
    return itemlist


def jayhap_search(item):
    logger.info("streamondemand.channels.trailertools jayhap_search")
    logger.info("adasd "+item.contentTitle)
    itemlist = []

    if item.extra != "jayhap":
        item.contentTitle += " trailer"
    texto = item.contentTitle
    post = urllib.urlencode({'q': texto, 'yt': 'true', 'vm': 'true', 'dm': 'true',
                             'v': 'all', 'l': 'all', 'd': 'all'})

    # Comprueba si es una búsqueda de cero o viene de la opción Siguiente
    if item.page != "":
        post += urllib.urlencode(item.page)
        data = scrapertools.downloadpage("https://www.jayhap.com/load_more.php", post=post)
    else:
        data = scrapertools.downloadpage("https://www.jayhap.com/get_results.php", post=post)
    data = jsontools.load_json(data)
    for video in data['videos']:
        url = video['url']
        server = video['source'].lower()
        duration = " (" + video['duration'] + ")"
        title = video['title'].decode("utf-8") + duration + "  [" + server.capitalize() + "]"
        thumbnail = video['thumbnail']
        if item.contextual:
            title = "[COLOR white]%s[/COLOR]" % title
        itemlist.append(item.clone(action="play", server=server, title=title, url=url, thumbnail=thumbnail,
                                   text_color="white"))

    if not itemlist:
        itemlist.append(item.clone(title="La búsqueda no ha dado resultados (%s)" % item.contentTitle,
                                   action="", thumbnail="", text_color=""))
    else:
        tokens = data['tokens']
        tokens['yt_token'] = tokens.pop('youtube')
        tokens['vm_token'] = tokens.pop('vimeo')
        tokens['dm_token'] = tokens.pop('dailymotion')
        itemlist.append(item.clone(title=">> Siguiente", page=tokens, action="jayhap_search", extra="jayhap",
                                   thumbnail="", text_color=""))

    if keyboard:
        title = "[COLOR green]%s[/COLOR]" if item.contextual else "%s"
        itemlist.append(item.clone(title=title % "Búsqueda Manual en Jayhap", action="manual_search",
                                   text_color="green", thumbnail="", extra="jayhap"))

    return itemlist
