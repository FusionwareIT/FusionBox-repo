# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# fusionse 5
# Copyright 2015 tvalacarta@gmail.com
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
# ------------------------------------------------------------
# This file is part of fusionse 5.
#
# fusionse 5 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# fusionse 5 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with fusionse 5.  If not, see <http://www.gnu.org/licenses/>.
# ------------------------------------------------------------
# Library Tools
# ------------------------------------------------------------

import errno
import math
import os
import sys
import urllib
import urllib2
from threading import Thread

import xbmc
from core import config
from core import filetools
from core import jsontools
from core import logger
from core import scrapertools

PLUGIN_NAME = "fusionse"

try:
    from core import tmdb
except:
    pass
from core.item import Item
from platformcode import platformtools

modo_cliente = int(config.get_setting("library_mode"))
# Host name where XBMC is running, leave as localhost if on this PC
# Make sure "Allow control of XBMC via HTTP" is set to ON in Settings ->
# Services -> Webserver
xbmc_host = config.get_setting("xbmc_host")
# Configured in Settings -> Services -> Webserver -> Port
xbmc_port = int(config.get_setting("xbmc_port"))
# Base URL of the json RPC calls. For GET calls we append a "request" URI
# parameter. For POSTs, we add the payload as JSON the the HTTP request body
xbmc_json_rpc_url = "http://" + xbmc_host + ":" + str(xbmc_port) + "/jsonrpc"

DEBUG = config.get_setting("debug")

FOLDER_LIBRARY = "/library" 
LIBRARY_PATH = xbmc.translatePath("special://profile/addon_data/plugin.video." + PLUGIN_NAME + FOLDER_LIBRARY)
if not filetools.exists(LIBRARY_PATH):
    logger.info("fusionse.platformcode.library Library path doesn't exist:" + LIBRARY_PATH)
    filetools.mkdir(LIBRARY_PATH)

# TODO permitir cambiar las rutas y nombres en settings para 'cine' y 'series'
FOLDER_MOVIES = "CINE"  # config.get_localized_string(30072)
MOVIES_PATH = filetools.join(LIBRARY_PATH, FOLDER_MOVIES)
if not filetools.exists(MOVIES_PATH):
    logger.info("fusionse.platformcode.library Movies path doesn't exist:" + MOVIES_PATH)
    filetools.mkdir(MOVIES_PATH)

FOLDER_TVSHOWS = "SERIES"  # config.get_localized_string(30073)
TVSHOWS_PATH = filetools.join(LIBRARY_PATH, FOLDER_TVSHOWS)
if not filetools.exists(TVSHOWS_PATH):
    logger.info("fusionse.platformcode.library Tvshows path doesn't exist:" + TVSHOWS_PATH)
    filetools.mkdir(TVSHOWS_PATH)

TVSHOW_FILE = "series.json"
TVSHOW_FILE_OLD = "series.xml"

# Versions compatible with JSONRPC v6
LIST_PLATFORM_COMPATIBLE = ["xbmc-frodo", "xbmc-gotham", "kodi-helix", "kodi-isengard", "kodi-jarvis"]

otmdb = None


def is_compatible():
    """
    comprueba si la plataforma es xbmc/Kodi, la version es compatible y si está configurada la libreria en Kodi.
    @rtype:   bool
    @return:  si es compatible.

    """
    logger.info("fusionse.platformcode.library is_compatible")
    # Si hemos dicho que nos busque la información de Kodi, damos por supuesto que está configurada su biblioteca
    if config.get_platform() in LIST_PLATFORM_COMPATIBLE and config.get_setting("get_metadata_from_kodi") == "true":
        return True
    else:
        return False


def save_library_movie(item):
    """
    guarda en la libreria de peliculas el elemento item, con los valores que contiene.
    @type item: item
    @param item: elemento que se va a guardar.
    @rtype insertados: int
    @return:  el número de elementos insertados
    @rtype sobreescritos: int
    @return:  el número de elementos sobreescritos
    @rtype fallidos: int
    @return:  el número de elementos fallidos o -1 si ha fallado todo
    """
    logger.info("fusionse.platformcode.library savelibrary_movie")
    insertados = 0
    sobreescritos = 0
    fallidos = 0
    logger.debug(item.tostring('\n'))

    # Itentamos obtener el titulo correcto:
    # 1. contentTitle: Este deveria ser el sitio correcto
    # 2. fulltitle
    # 3. title
    titulo = item.contentTitle
    if not titulo:
        titulo = item.fulltitle
    if not titulo:
        titulo = item.title

    # Colocamos el titulo en su sitio para que tmdb lo localize
    item.contentTitle = titulo

    # Si llegados a este punto no tenemos titulo, salimos
    if not item.contentTitle or not item.channel:
        return 0, 0, -1  # Salimos sin guardar
    # TODO configurar para segun el scraper se llamara a uno u otro
    tmdb.find_and_set_infoLabels_tmdb(item, config.get_setting("scrap_ask_name") == "true")

    # Llegados a este punto podemos tener:
    # Un item con infoLabels con la información actualizada de la peli
    # Un item sin información de la peli (se ha dado a cancelar en la ventana)

    # progress dialog
    p_dialog = platformtools.dialog_progress('fusionse', 'Aggiunta film...')
    filename = "{0} [{1}].strm".format(item.fulltitle.strip().lower(), item.channel)
    logger.debug(filename)
    fullfilename = filetools.join(MOVIES_PATH, filename)
    addon_name = sys.argv[0].strip()
    if not addon_name or addon_name.startswith("default.py"):
        addon_name = "plugin://plugin.video.fusionse/"

    if filetools.exists(fullfilename):
        logger.info("fusionse.platformcode.library savelibrary el fichero existe. Se sobreescribe")
        sobreescritos += 1
    else:
        insertados += 1

    p_dialog.update(100, 'Añadiendo película...', item.contentTitle)
    p_dialog.close()

    item.strm = True

    # Para depuración creamos un .json al lado del .strm, para poder visualizar que parametros se estan guardando
    filetools.write(fullfilename + ".json", item.tojson())

    if filetools.write(fullfilename, '{addon}?{url}'.format(addon=addon_name, url=item.tourl())):
        if 'tmdb_id' in item.infoLabels:
            create_nfo_file(item.infoLabels['tmdb_id'], fullfilename[:-5], "cine")
        else:
            if filetools.exists(fullfilename[:-5] + ".nfo"):
                filetools.remove(fullfilename[:-5] + ".nfo")

        # actualizamos la biblioteca de Kodi con la pelicula
        # TODO arreglar el porque hay que poner la ruta special
        ruta = "special://home/userdata/addon_data/plugin.video.fusionse/library/CINE/"
        update(ruta)

        return insertados, sobreescritos, fallidos
    else:
        return 0, 0, 1


def save_library_tvshow(item, episodelist):
    """
    guarda en la libreria de series la serie con todos los capitulos incluidos en la lista episodelist
    @type item: item
    @param item: item que representa la serie a guardar
    @type episodelist: list
    @param episodelist: listado de items que representan los episodios que se van a guardar.
    @rtype insertados: int
    @return:  el número de episodios insertados
    @rtype sobreescritos: int
    @return:  el número de episodios sobreescritos
    @rtype fallidos: int
    @return:  el número de episodios fallidos o -1 si ha fallado toda la serie
    """
    logger.info("fusionse.platformcode.library save_library_tvshow")

    # Itentamos obtener el titulo correcto:
    # 1. contentSerieName: Este deveria ser el sitio correcto
    # 2. show
    titulo = item.contentSerieName
    if not titulo:
        titulo = item.show

    # Colocamos el titulo en su sitio para que tmdb lo localize
    item.contentSerieName = titulo
    # establecemos "active" para que se actualice cuando se llame a library_service
    item.active = True

    # Si llegados a este punto no tenemos titulo, salimos
    if not item.contentSerieName or not item.channel:
        return 0, 0, -1  # Salimos sin guardar

    # TODO configurar para segun el scraper se llame a uno u otro
    tmdb.find_and_set_infoLabels_tmdb(item, config.get_setting("scrap_ask_name") == "true")

    path = filetools.join(TVSHOWS_PATH, "{0} [{1}]".format(item.contentSerieName.strip().lower(), item.channel).lower())
    if not filetools.exists(path):
        logger.info("fusionse.platformcode.library save_library_tvshow Creando directorio serie:" + path)
        try:
            filetools.mkdir(path)
        except OSError, exception:
            if exception.errno != errno.EEXIST:
                raise

    filetools.write(filetools.join(path, "tvshow.json"), item.tojson())

    if 'tmdb_id' in item.infoLabels:
        create_nfo_file(item.infoLabels['tmdb_id'], path, "serie")
    else:
        if filetools.exists(filetools.join(path, "tvshow.nfo")):
            filetools.remove(filetools.join(path, "tvshow.nfo"))

    # Guardar los episodios
    insertados, sobreescritos, fallidos = save_library_episodes(path, episodelist, item)

    return insertados, sobreescritos, fallidos


def save_library_episodes(path, episodelist, serie, silent=False):
    """
    guarda en la ruta indicada todos los capitulos incluidos en la lista episodelist
    @type path: str
    @param path: ruta donde guardar los episodios
    @type episodelist: list
    @param episodelist: listado de items que representan los episodios que se van a guardar.
    @type serie: item
    @param serie: serie de la que se van a guardar los episodios
    @type silent: bool
    @param silent: establece si se muestra la notificación
    @rtype insertados: int
    @return:  el número de episodios insertados
    @rtype sobreescritos: int
    @return:  el número de episodios sobreescritos
    @rtype fallidos: int
    @return:  el número de episodios fallidos
    """
    logger.info("fusionse.platformcode.library save_library_episodes")

    # No hay lista de episodios, no hay nada que guardar
    if not len(episodelist):
        logger.info("fusionse.platformcode.library save_library_episodes No hay lista de episodios, "
                    "salimos sin crear strm")
        return 0, 0, 0
    insertados = 0
    sobreescritos = 0
    fallidos = 0

    # Silent es para no mostrar progreso (para library_service)
    if not silent:
        # progress dialog
        p_dialog = platformtools.dialog_progress('fusionse', 'Aggiunta episodi...')
        p_dialog.update(0, 'Aggiunta episodio...')

    # fix float porque la division se hace mal en python 2.x
    t = float(100) / len(episodelist)

    addon_name = sys.argv[0].strip()
    if not addon_name or addon_name.startswith("default.py"):
        addon_name = "plugin://plugin.video.fusionse/"

    for i, e in enumerate(episodelist):
        if not silent:
            p_dialog.update(int(math.ceil((i + 1) * t)), 'Aggiunta episodio...', e.title)
        # Añade todos menos el que dice "Añadir esta serie..." o "Descargar esta serie..."
        if e.action == "add_serie_to_library" or e.action == "download_all_episodes":
            continue

        season_episode = scrapertools.get_season_and_episode(e.title.lower())
        e.infoLabels = serie.infoLabels
        e.contentSeason, e.contentEpisodeNumber = season_episode.split("x")

        filename = "{0}.strm".format(season_episode)
        fullfilename = filetools.join(path, filename)

        nuevo = not filetools.exists(fullfilename)
        if e.infoLabels.get("tmdb_id"):
            tmdb.find_and_set_infoLabels_tmdb(e, config.get_setting("scrap_ask_name") == "true")

        e.strm = True

        # Para depuración creamos un .json al lado del .strm, para poder visualizar que parametros se estan guardando
        filetools.write(fullfilename + ".json", e.tojson())

        # TODO fix temporal, en algunas ocasiones no se reproduce desde la biblioteca de kodi si tiene valor
        # por ejemplo serie doctor who, en seriesblanco
        e.infoLabels['tmdb_id'] = ""

        if filetools.write(fullfilename, '{addon}?{url}'.format(addon=addon_name, url=e.tourl())):
            if nuevo:
                insertados += 1
            else:
                sobreescritos += 1
        else:
            fallidos += 1

        if not silent and p_dialog.iscanceled():
            break

    if not silent:
        p_dialog.close()

    # si se han añadido episodios los actualizamos en la biblioteca de Kodi con la serie
    if fallidos >= 0:
        # TODO arreglar el porque hay que poner la ruta special
        ruta = "special://home/userdata/addon_data/plugin.video.fusionse/library/SERIES/" + \
               "{0} [{1}]".format(serie.contentSerieName.strip().lower(), serie.channel).lower() + "/"
        update(ruta)

    logger.debug("insertados= {0}, sobreescritos={1}, fallidos={2}".format(insertados, sobreescritos, fallidos))
    return insertados, sobreescritos, fallidos


def set_infolabels_from_library(itemlist, tipo):
    """
    guarda los datos (thumbnail, fanart, plot, actores, etc) a mostrar de la library de Kodi.
    @type itemlist: list
    @param itemlist: item
    @type tipo: str
    @param tipo:
    @rtype:   infoLabels
    @return:  result of saving.
    """
    logger.info("fusionse.platformcode.library set_infoLabels_from_library")

    # Metodo 1: De la bilioteca de pelisalacarta
    if tipo == 'Movies':
        for item in itemlist:
            if item.path.endswith(".strm"):
                data_file = item.path
                if filetools.exists(data_file):
                    infolabels = Item().fromurl(filetools.read(data_file)).infoLabels
                    item.infoLabels = infolabels
            else:
                data_file = os.path.splitext(item.path)[0] + ".json"
                if filetools.exists(data_file):
                    infolabels = Item().fromjson(filetools.read(data_file)).infoLabels
                    item.infoLabels = infolabels

            item.title = item.contentTitle
            item.plot = item.contentPlot
            item.thumbnail = item.contentThumbnail

    elif tipo == 'TVShows':
        for item in itemlist:
            data_file = filetools.join(item.path, "tvshow.json")
            if filetools.exists(data_file):
                infolabels = Item().fromjson(filetools.read(data_file)).infoLabels
                item.infoLabels = infolabels

            item.title = item.contentSerieName
            item.thumbnail = item.contentThumbnail
            item.plot = item.contentPlot

    elif tipo == 'Episodes':
        for item in itemlist:
            if item.path.endswith(".strm"):
                data_file = item.path
                if filetools.exists(data_file):
                    infolabels = Item().fromurl(filetools.read(data_file)).infoLabels
                    item.infoLabels = infolabels
            # TODO debería existir el else?
            else:
                data_file = os.path.splitext(item.path)[0] + ".json"
                if filetools.exists(data_file):
                    infolabels = Item().fromjson(filetools.read(data_file)).infoLabels
                    item.infoLabels = infolabels

            item.plot = item.contentPlot
            item.thumbnail = item.contentThumbnail

            if item.contentTitle:
                if len(str(item.contentEpisodeNumber)) == 1:
                    item.title = "{0}x0{1}".format(item.contentSeason, item.contentEpisodeNumber)
                else:
                    item.title = "{0}x{1}".format(item.contentSeason, item.contentEpisodeNumber)

                item.title = "{0} - {1}".format(item.title, item.contentTitle.strip())
            else:
                if "fulltitle" in item:
                    item.title = item.fulltitle
                else:
                    if len(str(item.contentEpisodeNumber)) == 1:
                        item.title = "{0}x0{1}".format(item.contentSeason, item.contentEpisodeNumber)
                    else:
                        item.title = "{0}x{1}".format(item.contentSeason, item.contentEpisodeNumber)

                    item.title = "{0} - {1}".format(item.title, "Episodio {0}".format(item.contentEpisodeNumber))

    if config.get_setting("get_metadata_from_kodi") == "true":
        # Metodo2: De la bilioteca de kodi
        payload = dict()
        result = list()

        if tipo == 'Movies':
            payload = {"jsonrpc": "2.0",
                       "method": "VideoLibrary.GetMovies",
                       "params": {"properties": ["title", "year", "rating", "trailer", "tagline", "plot", "plotoutline",
                                                 "originaltitle", "lastplayed", "playcount", "writer", "mpaa", "cast",
                                                 "imdbnumber", "runtime", "set", "top250", "votes", "fanart", "tag",
                                                 "thumbnail", "file", "director", "country", "studio", "genre",
                                                 "sorttitle", "setid", "dateadded"
                                                 ]},
                       "id": "libMovies"}

        elif tipo == 'TVShows':
            payload = {"jsonrpc": "2.0",
                       "method": "VideoLibrary.GetTVShows",
                       "params": {"properties": ["title", "genre", "year", "rating", "plot", "studio", "mpaa", "cast",
                                                 "playcount", "episode", "imdbnumber", "premiered", "votes",
                                                 "lastplayed", "fanart", "thumbnail", "file", "originaltitle",
                                                 "sorttitle", "episodeguide", "season", "watchedepisodes", "dateadded",
                                                 "tag"]},
                       "id": "libTvShows"}

        elif tipo == 'Episodes' and 'tvshowid' in itemlist[0].infoLabels and itemlist[0].infoLabels['tvshowid']:
            tvshowid = itemlist[0].infoLabels['tvshowid']
            payload = {"jsonrpc": "2.0",
                       "method": "VideoLibrary.GetEpisodes",
                       "params": {"tvshowid": tvshowid,
                                  "properties": ["title", "plot", "votes", "rating", "writer", "firstaired",
                                                 "playcount", "runtime", "director", "productioncode", "season",
                                                 "episode", "originaltitle", "showtitle", "cast", "lastplayed",
                                                 "fanart", "thumbnail", "file", "dateadded", "tvshowid"]},
                       "id": 1}

        data = get_data(payload)
        logger.debug("JSON-RPC: {0}".format(data))

        if 'error' in data:
            logger.error("JSON-RPC: {0}".format(data))

        elif 'movies' in data['result']:
            result = data['result']['movies']

        elif 'tvshows' in data['result']:
            result = data['result']['tvshows']

        elif 'episodes' in data['result']:
            result = data['result']['episodes']

        if result:
            for i in itemlist:
                for r in result:

                    if r['file'].endswith(os.sep) or r['file'].endswith('/'):
                        r_filename_aux = r['file'][:-1]
                    else:
                        r_filename_aux = r['file']

                    # r_filename_aux = r['file'][:-1] if r['file'].endswith(os.sep) or r['file'].endswith('/') else r['file']
                    r_filename = os.path.basename(r_filename_aux)
                    # logger.debug(os.path.basename(i.path) + '\n' + r_filename)
                    i_filename = os.path.basename(i.path)
                    if i_filename == r_filename:
                        infolabels = r

                        # Obtener imagenes y asignarlas al item
                        if 'thumbnail' in infolabels:

                            infolabels['thumbnail'] = urllib.unquote_plus(infolabels['thumbnail']).replace('image://',
                                                                                                           '')

                            if infolabels['thumbnail'].endswith('/'):
                                i.thumbnail = infolabels['thumbnail'][:-1]
                            else:
                                i.thumbnail = infolabels['thumbnail']

                                # i.thumbnail = infolabels['thumbnail'][:-1] if infolabels['thumbnail'].endswith('/') else infolabels['thumbnail']

                        if 'fanart' in infolabels:

                            infolabels['fanart'] = urllib.unquote_plus(infolabels['fanart']).replace('image://', '')

                            if infolabels['fanart'].endswith('/'):
                                i.fanart = infolabels['fanart'][:-1]
                            else:
                                i.fanart = infolabels['fanart']

                                # i.fanart = infolabels['fanart'][:-1] if infolabels['fanart'].endswith('/') else infolabels['fanart']

                        # Adaptar algunos campos al formato infoLables
                        if 'cast' in infolabels:
                            l_castandrole = list()
                            for c in sorted(infolabels['cast'], key=lambda _c: _c["order"]):
                                l_castandrole.append((c['name'], c['role']))
                            infolabels.pop('cast')
                            infolabels['castandrole'] = l_castandrole
                        if 'genre' in infolabels:
                            infolabels['genre'] = ', '.join(infolabels['genre'])
                        if 'writer' in infolabels:
                            infolabels['writer'] = ', '.join(infolabels['writer'])
                        if 'director' in infolabels:
                            infolabels['director'] = ', '.join(infolabels['director'])
                        if 'country' in infolabels:
                            infolabels['country'] = ', '.join(infolabels['country'])
                        if 'studio' in infolabels:
                            infolabels['studio'] = ', '.join(infolabels['studio'])
                        if 'runtime' in infolabels:
                            infolabels['duration'] = infolabels.pop('runtime')

                        # Fijar el titulo si existe y añadir infoLabels al item
                        if 'label' in infolabels:
                            i.title = infolabels['label']
                        i.infoLabels = infolabels
                        result.remove(r)
                        break


def mark_as_watched(item):
    Thread(target=mark_as_watched_on_strm, args=[item]).start()
    Thread(target=mark_as_watched_on_kodi, args=[item]).start()


def mark_as_watched_on_strm(item):
    """
    Marca un .strm como "visto" añadiendo el parametro "playcount" a los infoLabels del strm.
    @param item: item que queremos marcar como visto
    @type item: item
    """
    logger.info("fusionse.platformcode.library mark_as_watched_on_strm")
    if not config.get_setting("mark_as_watched") == "true":
        return

    xbmc.sleep(5000)

    while xbmc.Player().isPlaying():
        tiempo_actual = xbmc.Player().getTime()
        totaltime = xbmc.Player().getTotalTime()
        condicion = int(config.get_setting("watched_setting"))

        if condicion == 0:  # '5 minutos'
            mark_time = 300
        elif condicion == 1:  # '30%'
            mark_time = totaltime * 0.3
        elif condicion == 2:  # '50%'
            mark_time = totaltime * 0.5
        elif condicion == 3:  # '80%'
            mark_time = totaltime * 0.8

        logger.debug(str(mark_time))

        if tiempo_actual > mark_time:
            strm = Item().fromurl(filetools.read(item.path))
            if not type(strm.infoLabels) == dict:
                strm.infoLabels = {}
            strm.infoLabels["playcount"] = 1
            addon_name = sys.argv[0].strip()

            if not addon_name:
                addon_name = "plugin://plugin.video.pelisalacarta/"

            filetools.write(item.path + ".json", strm.tojson())
            filetools.write(item.path, '{addon}?{url}'.format(addon=addon_name, url=strm.tourl()))
            break

        xbmc.sleep(30000)


def mark_as_watched_on_kodi(item):
    """
    marca el capitulo como visto en la libreria de Kodi
    @type item: item
    @param item: elemento a marcar como visto
    """
    logger.info("pelisalacarta.platformcode.library mark_as_watched_on_kodi")
    # logger.info("item mark_as_watched_on_kodi {}".format(item.tostring()))
    video_id = 0
    category = ''
    if 'infoLabels' in item:
        if 'episodeid' in item.infoLabels and item.infoLabels['episodeid']:
            category = 'Series'
            video_id = item.infoLabels['episodeid']

        elif 'movieid' in item.infoLabels and item.infoLabels['movieid']:
            category = 'Movies'
            video_id = item.infoLabels['movieid']

        else:
            if hasattr(item, "show") or hasattr(item, "contentSerieName"):
                category = 'Series'

    else:
        if hasattr(item, "show") or hasattr(item, "contentSerieName"):
            category = 'Series'

    logger.info("se espera 5 segundos por si falla al reproducir el fichero")
    xbmc.sleep(5000)

    if not is_compatible() or not config.get_setting("mark_as_watched") == "true":
        return

    if xbmc.Player().isPlaying():
        payload = {"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}
        data = get_data(payload)

        if 'result' in data:
            payload_f = ''
            player_id = data['result'][0]["playerid"]

            if category == "Series":
                episodeid = video_id
                if episodeid == 0:
                    payload = {"jsonrpc": "2.0", "params": {"playerid": player_id,
                                                            "properties": ["season", "episode", "file", "showtitle"]},
                               "method": "Player.GetItem", "id": "libGetItem"}

                    data = get_data(payload)
                    if 'result' in data:
                        season = data['result']['item']['season']
                        episode = data['result']['item']['episode']
                        showtitle = data['result']['item']['showtitle']
                        # logger.info("titulo es {0}".format(showtitle))

                        payload = {
                            "jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes",
                            "params": {
                                "filter": {"and": [{"field": "season", "operator": "is", "value": str(season)},
                                                   {"field": "episode", "operator": "is", "value": str(episode)}]},
                                "properties": ["title", "plot", "votes", "rating", "writer", "firstaired", "playcount",
                                               "runtime", "director", "productioncode", "season", "episode",
                                               "originaltitle", "showtitle", "lastplayed", "fanart", "thumbnail",
                                               "file", "resume", "tvshowid", "dateadded", "uniqueid"]},
                            "id": 1}

                        data = get_data(payload)
                        if 'result' in data:
                            for d in data['result']['episodes']:
                                if d['showtitle'] == showtitle:
                                    episodeid = d['episodeid']
                                    break

                if episodeid != 0:
                    payload_f = {"jsonrpc": "2.0", "method": "VideoLibrary.SetEpisodeDetails", "params": {
                        "episodeid": episodeid, "playcount": 1}, "id": 1}

            else:  # Categoria == 'Movies'
                movieid = video_id
                if movieid == 0:

                    payload = {"jsonrpc": "2.0", "method": "Player.GetItem",
                               "params": {"playerid": 1,
                                          "properties": ["year", "file", "title", "uniqueid", "originaltitle"]},
                               "id": "libGetItem"}

                    data = get_data(payload)
                    logger.debug(repr(data))
                    if 'result' in data:
                        title = data['result']['item']['title']
                        year = data['result']['item']['year']
                        # logger.info("titulo es {0}".format(title))

                        payload = {"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies",
                                   "params": {
                                       "filter": {"and": [{"field": "title", "operator": "is", "value": title},
                                                          {"field": "year", "operator": "is", "value": str(year)}]},
                                       "properties": ["title", "plot", "votes", "rating", "writer", "playcount",
                                                      "runtime", "director", "originaltitle", "lastplayed", "fanart",
                                                      "thumbnail", "file", "resume", "dateadded"]},
                                   "id": 1}

                        data = get_data(payload)

                        if 'result' in data:
                            for d in data['result']['movies']:
                                logger.info("title {0}".format(d['title']))
                                if d['title'] == title:
                                    movieid = d['movieid']
                                    break

                if movieid != 0:
                    payload_f = {"jsonrpc": "2.0", "method": "VideoLibrary.SetMovieDetails", "params": {
                        "movieid": movieid, "playcount": 1}, "id": 1}

            if payload_f:
                condicion = int(config.get_setting("watched_setting"))
                payload = {"jsonrpc": "2.0", "method": "Player.GetProperties",
                           "params": {"playerid": player_id,
                                      "properties": ["time", "totaltime", "percentage"]},
                           "id": 1}

                while xbmc.Player().isPlaying():
                    data = get_data(payload)
                    # logger.debug("Player.GetProperties: {0}".format(data))
                    # 'result': {'totaltime': {'hours': 0, 'seconds': 13, 'minutes': 41, 'milliseconds': 341},
                    #            'percentage': 0.209716334939003,
                    #            'time': {'hours': 0, 'seconds': 5, 'minutes': 0, 'milliseconds': 187}}

                    if 'result' in data:
                        from datetime import timedelta
                        totaltime = data['result']['totaltime']
                        totaltime = totaltime['seconds'] + 60 * totaltime['minutes'] + 3600 * totaltime['hours']
                        tiempo_actual = data['result']['time']
                        tiempo_actual = timedelta(hours=tiempo_actual['hours'], minutes=tiempo_actual['minutes'],
                                                  seconds=tiempo_actual['seconds'])

                        if condicion == 0:  # '5 minutos'
                            mark_time = timedelta(seconds=300)
                        elif condicion == 1:  # '30%'
                            mark_time = timedelta(seconds=totaltime * 0.3)
                        elif condicion == 2:  # '50%'
                            mark_time = timedelta(seconds=totaltime * 0.5)
                        elif condicion == 3:  # '80%'
                            mark_time = timedelta(seconds=totaltime * 0.8)

                        logger.debug(str(mark_time))

                        if tiempo_actual > mark_time:
                            # Marcar como visto
                            data = get_data(payload_f)
                            if data['result'] != 'OK':
                                logger.info("ERROR al poner el contenido como visto")
                            break

                    xbmc.sleep(30000)


def get_data(payload):
    """
    obtiene la información de la llamada JSON-RPC con la información pasada en payload
    @type payload: dict
    @param payload: data
    :return:
    """
    logger.info("fusionse.platformcode.library get_data:: payload {0}".format(payload))
    # Required header for XBMC JSON-RPC calls, otherwise you'll get a 415 HTTP response code - Unsupported media type
    headers = {'content-type': 'application/json'}

    if modo_cliente:
        try:
            req = urllib2.Request(xbmc_json_rpc_url, data=jsontools.dump_json(payload), headers=headers)
            f = urllib2.urlopen(req)
            response = f.read()
            f.close()

            logger.info("fusionse.platformcode.library get_data:: response {0}".format(response))
            data = jsontools.load_json(response)
        except Exception, ex:
            template = "An exception of type {0} occured. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            logger.info(
                "fusionse.platformcode.library get_data:: error en xbmc_json_rpc_url: {0}".format(message))
            data = ["error"]
    else:
        try:
            data = jsontools.load_json(xbmc.executeJSONRPC(jsontools.dump_json(payload)))
        except Exception, ex:
            template = "An exception of type {0} occured. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            logger.info("fusionse.platformcode.library get_data:: error en xbmc.executeJSONRPC: {0}".
                        format(message))
            data = ["error"]

    logger.info("fusionse.platformcode.library get_data:: data {0}".format(data))

    return data


def update(_path):
    """
    actualiza la libreria

    @type path: str
    @param path: ruta que hay que actualizar en la libreria
    """
    logger.info("fusionse.platformcode.library update")
    # Se comenta la llamada normal para reutilizar 'payload' dependiendo del modo cliente
    # xbmc.executebuiltin('UpdateLibrary(video)')
    if _path:
        payload = {"jsonrpc": "2.0", "method": "VideoLibrary.Scan", "params": {"directory": _path}, "id": 1}
    else:
        payload = {"jsonrpc": "2.0", "method": "VideoLibrary.Scan", "id": 1}
    data = get_data(payload)
    logger.info("fusionse.platformcode.library update data:{0}".format(data))


def clean():
    """
    limpia la libreria de elementos que no existen
    """
    logger.info("fusionse.platformcode.library clean")
    # Se comenta la llamada normal para reutilizar 'payload' dependiendo del modo cliente
    # xbmc.executebuiltin("CleanLibrary(video)")
    payload = {"jsonrpc": "2.0", "method": "VideoLibrary.Clean", "id": 1}
    data = get_data(payload)
    logger.info("fusionse.platformcode.library clean data:{0}".format(data))


def create_nfo_file(video_id, path, type_video):
    """
    crea el fichero nfo con la información para scrapear la pelicula o serie
    @type video_id: str
    @param video_id: codigo identificativo del video
    @type path: str
    @param path: ruta donde se creará el fichero
    @type type_video: str
    @param type_video: tipo de video "serie" o "pelicula"
    """
    # TODO meter un parametro más "scraper" para elegir entre una lista: imdb, tvdb, etc... y con el video_id pasado de
    # esa pagina se genere el nfo especifico
    logger.info("fusionse.platformcode.library create_nfo_file")

    if type_video == "serie":
        data = "https://www.themoviedb.org/tv/{0}".format(video_id)
        nfo_file = filetools.join(path, "tvshow.nfo")
    else:
        data = "https://www.themoviedb.org/movie/{0}".format(video_id)
        nfo_file = path + ".nfo"

    filetools.write(nfo_file, data)


def add_pelicula_to_library(item):
    logger.info("fusionse.platformcode.library add_pelicula_to_library")

    new_item = item.clone(action="findvideos")
    insertados, sobreescritos, fallidos = save_library_movie(new_item)

    if fallidos == 0:
        platformtools.dialog_ok("Libreria", "Il film è stato aggiunto alla libreria")
    else:
        itemlist.append(Item(title="ERRORE, il film non è stato aggiunto alla libreria", channel=item.channel))
        platformtools.dialog_ok("Libreria", "ERRORE, il film non è stato aggiunto alla libreria")


def add_serie_to_library(item, channel):
    logger.info("fusionse.platformcode.library add_serie_to_library, show=#" + item.show + "#")

    # Esta marca es porque el item tiene algo más aparte en el atributo "extra"
    item.action = item.extra
    if "###" in item.extra:
        item.action = item.extra.split("###")[0]
        item.extra = item.extra.split("###")[1]

    if item.from_action:
        item.__dict__["action"] = item.__dict__.pop("from_action")
    if item.from_channel:
        item.__dict__["channel"] = item.__dict__.pop("from_channel")

    # Obtiene el listado desde el que se llamó
    itemlist = getattr(channel, item.action)(item)

    insertados, sobreescritos, fallidos = save_library_tvshow(item, itemlist)

    if fallidos == -1:
        platformtools.dialog_ok("Biblioteca", "ERRORE, la serie non è stata aggiunta alla libreria")
        logger.error("La serie {0} no se ha podido añadir a la biblioteca".format(item.show))

    elif fallidos > 0:
        platformtools.dialog_ok("Libreria", "ERRORE, la serie non è stata aggiunta completamente alla libreria")
        logger.error("No se han podido añadir {0} episodios de la serie {1} a la biblioteca".format(fallidos,
                                                                                                    item.show))
    else:
        platformtools.dialog_ok("Libreria", "La serie è stata aggiunta alla libreria")
        logger.info("[launcher.py] Se han añadido {0} episodios de la serie {1} a la biblioteca".format(insertados,
                                                                                                        item.show))
