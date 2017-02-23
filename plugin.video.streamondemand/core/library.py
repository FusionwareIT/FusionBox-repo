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
# ------------------------------------------------------------
# Common Library Tools
# ------------------------------------------------------------

import errno
import math

from core import config
from core import filetools
from core import logger
from core import scrapertools
from core import scraper
from core.item import Item
from platformcode import platformtools

LIBRARY_PATH = config.get_library_path()
if config.get_setting("folder_movies") != "":
    FOLDER_MOVIES = config.get_setting("folder_movies")
else:
    FOLDER_MOVIES = "CINE"  # config.get_localized_string(30072)
if config.get_setting("folder_tvshows") != "":
    FOLDER_TVSHOWS = config.get_setting("folder_tvshows")
else:
    FOLDER_TVSHOWS = "SERIES"  # config.get_localized_string(30073)
MOVIES_PATH = filetools.join(LIBRARY_PATH, FOLDER_MOVIES)
TVSHOWS_PATH = filetools.join(LIBRARY_PATH, FOLDER_TVSHOWS)
logger.info("LIBRARY_PATH (RAW): " + LIBRARY_PATH)
# logger.info("MOVIES_PATH (RAW): " + MOVIES_PATH)
# logger.info("TVSHOWS_PATH (RAW): " + TVSHOWS_PATH)
logger.info("FOLDER_MOVIES (RAW): " + FOLDER_MOVIES)
logger.info("FOLDER_TVSHOWS (RAW): " + FOLDER_TVSHOWS)

addon_name = "plugin://plugin.video.streamondemand/"

# TODO: mover todo esto a config.verify_directories_created()
if not filetools.exists(LIBRARY_PATH):
    logger.info("Library path doesn't exist:" + LIBRARY_PATH)
    config.verify_directories_created()

if not filetools.exists(MOVIES_PATH):
    logger.info("Movies path doesn't exist:" + MOVIES_PATH)
    if filetools.mkdir(MOVIES_PATH) and config.is_xbmc():
        if config.is_xbmc():
            from platformcode import xbmc_library

            xbmc_library.establecer_contenido(FOLDER_MOVIES)

if not filetools.exists(TVSHOWS_PATH):
    logger.info("Tvshows path doesn't exist:" + TVSHOWS_PATH)
    if filetools.mkdir(TVSHOWS_PATH) and config.is_xbmc():
        if config.is_xbmc():
            from platformcode import xbmc_library

            xbmc_library.establecer_contenido(FOLDER_TVSHOWS)


def read_nfo(path_nfo, item=None):
    """
    Metodo para leer archivos nfo.
        Los arcivos nfo tienen la siguiente extructura: url_scraper | xml + item_json
        [url_scraper] y [xml] son opcionales, pero solo uno de ellos ha de existir siempre.
    @param path_nfo: ruta absoluta al archivo nfo
    @type path_nfo: str
    @param item: Si se pasa este parametro el item devuelto sera una copia de este con
        los valores de 'infoLabels', 'library_playcounts' y 'path' leidos del nfo
    @type: Item
    @return: Una tupla formada por la cabecera (head_nfo ='url_scraper'|'xml') y el objeto 'item_json'
    @rtype: tuple (str, Item)
    """
    head_nfo = ""
    it = None

    data = filetools.read(path_nfo)

    if data:
        head_nfo = data.splitlines()[0] + "\n"
        data = "\n".join(data.splitlines()[1:])

        if not head_nfo.startswith('http'):
            # url_scraper no valida, xml presente
            head_nfo = ''  # TODO devolver el xml en head_nfo
            import re
            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
            data = re.sub("(<tvshow>|<movie>)(.*?)(</tvshow>|</movie>)", "", data)

        it_nfo = Item().fromjson(data)

        if item:
            it = item.clone()
            it.infoLabels = it_nfo.infoLabels
            if 'library_playcounts' in it_nfo:
                it.library_playcounts = it_nfo.library_playcounts
            if it_nfo.path:
                it.path = it_nfo.path
        else:
            it = it_nfo

        if 'fanart' in it.infoLabels:
            it.fanart = it.infoLabels['fanart']

    return head_nfo, it


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
    logger.info()
    # logger.debug(item.tostring('\n'))
    insertados = 0
    sobreescritos = 0
    fallidos = 0
    path = ""

    # Itentamos obtener el titulo correcto:
    # 1. contentTitle: Este deberia ser el sitio correcto, ya que title suele contener "Añadir a la biblioteca..."
    # 2. fulltitle
    # 3. title
    if not item.contentTitle:
        # Colocamos el titulo correcto en su sitio para que scraper lo localize
        if item.fulltitle:
            item.contentTitle = item.fulltitle
        else:
            item.contentTitle = item.title

    # Si llegados a este punto no tenemos titulo, salimos
    if not item.contentTitle or not item.channel:
        logger.debug("NO ENCONTRADO contentTitle")
        return 0, 0, -1  # Salimos sin guardar

    # TODO configurar para segun el scraper se llamara a uno u otro
    scraper_return = scraper.find_and_set_infoLabels(item)

    # Llegados a este punto podemos tener:
    #  scraper_return = True: Un item con infoLabels con la información actualizada de la peli
    #  scraper_return = False: Un item sin información de la peli (se ha dado a cancelar en la ventana)
    #  item.infoLabels['code'] == "" : No se ha encontrado el identificador de IMDB necesario para continuar, salimos
    if not scraper_return or not item.infoLabels['code']:
        # TODO de momento si no hay resultado no añadimos nada,
        # aunq podriamos abrir un cuadro para introducir el identificador/nombre a mano
        logger.debug("NO ENCONTRADO EN SCRAPER O NO TIENE IMDB_ID")
        return 0, 0, -1

    _id = item.infoLabels['code']

    # progress dialog
    p_dialog = platformtools.dialog_progress('streamondemand', 'Aggiunta film...')

    base_name = filetools.validate_path(item.contentTitle).lower()

    for raiz, subcarpetas, ficheros in filetools.walk(MOVIES_PATH):
        for c in subcarpetas:
            if c.endswith("[%s]" % _id):
                path = filetools.join(raiz, c)
                break

    if not path:
        # Crear carpeta
        path = filetools.join(MOVIES_PATH, ("%s [%s]" % (base_name, _id)).strip())
        logger.info("Creando directorio pelicula:" + path)
        if not filetools.mkdir(path):
            logger.debug("No se ha podido crear el directorio")
            return 0, 0, -1

    nfo_path = filetools.join(path, "%s [%s].nfo" % (base_name, _id))
    strm_path = filetools.join(path, "%s.strm" % base_name)
    json_path = filetools.join(path, ("%s [%s].json" % (base_name, item.channel.lower())))

    nfo_exists = filetools.exists(nfo_path)
    strm_exists = filetools.exists(strm_path)
    json_exists = filetools.exists(json_path)

    if not nfo_exists:
        # Creamos .nfo si no existe
        logger.info("Creando .nfo: " + nfo_path)
        if item.infoLabels['tmdb_id']:
            head_nfo = "https://www.themoviedb.org/movie/%s\n" % item.infoLabels['tmdb_id']
        else:
            head_nfo = "Aqui ira el xml"  # TODO

        item_nfo = Item(title=item.contentTitle, channel="biblioteca", action='findvideos',
                        library_playcounts={"%s [%s]" % (base_name, _id): 0}, infoLabels=item.infoLabels,
                        library_urls={})

    else:
        # Si existe .nfo, pero estamos añadiendo un nuevo canal lo abrimos
        head_nfo, item_nfo = read_nfo(nfo_path)

    if not strm_exists:
        # Crear base_name.strm si no existe
        item_strm = item.clone(channel='biblioteca', action='play_from_library',
                               strm_path=strm_path.replace(MOVIES_PATH, ""), contentType='movie',
                               infoLabels={'title': item.contentTitle})
        strm_exists = filetools.write(strm_path, '%s?%s' % (addon_name, item_strm.tourl()))
        item_nfo.strm_path = strm_path.replace(MOVIES_PATH, "")

    # Solo si existen item_nfo y .strm continuamos
    if item_nfo and strm_exists:

        if json_exists:
            logger.info("El fichero existe. Se sobreescribe")
            sobreescritos += 1
        else:
            insertados += 1

        if filetools.write(json_path, item.tojson()):
            p_dialog.update(100, 'Añadiendo película...', item.contentTitle)
            item_nfo.library_urls[item.channel] = item.url

            if filetools.write(nfo_path, head_nfo + item_nfo.tojson()):
                # actualizamos la biblioteca de Kodi con la pelicula
                if config.is_xbmc():
                    from platformcode import xbmc_library
                    xbmc_library.update(FOLDER_MOVIES, filetools.basename(path) + "/")

                p_dialog.close()
                return insertados, sobreescritos, fallidos

    # Si llegamos a este punto es por q algo ha fallado
    logger.error("No se ha podido guardar %s en la biblioteca" % item.contentTitle)
    p_dialog.update(100, 'Fallo al añadir...', item.contentTitle)
    p_dialog.close()
    # TODO habria q poner otra advertencia?
    return 0, 0, -1


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
    logger.info()
    # logger.debug(item.tostring('\n'))
    path = ""

    # Si llegados a este punto no tenemos titulo o tmdb_id, salimos
    if not (item.contentSerieName or item.infoLabels['tmdb_id']) or not item.channel:
        logger.debug("NO ENCONTRADO contentSerieName NI tmdb_id")
        return 0, 0, -1  # Salimos sin guardar

    # TODO configurar para segun el scraper se llame a uno u otro
    scraper_return = scraper.find_and_set_infoLabels(item)

    # Llegados a este punto podemos tener:
    #  scraper_return = True: Un item con infoLabels con la información actualizada de la serie
    #  scraper_return = False: Un item sin información de la peli (se ha dado a cancelar en la ventana)
    #  item.infoLabels['code'] == "" : No se ha encontrado el identificador de IMDB necesario para continuar, salimos
    if not scraper_return or not item.infoLabels['code']:
        # TODO de momento si no hay resultado no añadimos nada,
        # aunq podriamos abrir un cuadro para introducir el identificador/nombre a mano
        logger.debug("NO ENCONTRADO EN SCRAPER O NO TIENE IMDB_ID")
        return 0, 0, -1

    _id = item.infoLabels['code']
    if config.get_setting("original_title_folder", "biblioteca") == 1 and item.infoLabels['originaltitle']:
        base_name = item.infoLabels['originaltitle']
    elif item.infoLabels['title']:
        base_name = item.infoLabels['title']
    else:
        base_name = item.contentSerieName

    base_name = filetools.validate_path(base_name.replace('/', '-')).lower()

    for raiz, subcarpetas, ficheros in filetools.walk(TVSHOWS_PATH):
        for c in subcarpetas:
            if c.endswith("[%s]" % _id):
                path = filetools.join(raiz, c)
                break

    if not path:
        path = filetools.join(TVSHOWS_PATH, ("%s [%s]" % (base_name, _id)).strip())
        logger.info("Creando directorio serie: " + path)
        try:
            filetools.mkdir(path)
        except OSError, exception:
            if exception.errno != errno.EEXIST:
                raise

    # Eliminamos de la lista lo que no sean episodios
    for it in episodelist:
        if not scrapertools.get_season_and_episode(it.title):
            episodelist.remove(it)

    tvshow_path = filetools.join(path, "tvshow.nfo")
    if not filetools.exists(tvshow_path):
        # Creamos tvshow.nfo, si no existe, con la head_nfo, info de la serie y marcas de episodios vistos
        logger.info("Creando tvshow.nfo: " + tvshow_path)
        if item.infoLabels['url_scraper']:
            # head_nfo = "https://www.themoviedb.org/tv/%s\n" % item.infoLabels['tmdb_id']
            head_nfo = item.infoLabels['url_scraper'] + "\n"
        else:
            head_nfo = "Aqui ira el xml"  # TODO

        item_tvshow = Item(title=item.contentTitle, channel="biblioteca", action="get_temporadas",
                           fanart=item.infoLabels['fanart'], thumbnail=item.infoLabels['thumbnail'],
                           infoLabels=item.infoLabels, path=path.replace(TVSHOWS_PATH, ""))
        item_tvshow.library_playcounts = {}
        item_tvshow.library_urls = {item.channel: item.url}

    else:
        # Si existe tvshow.nfo, pero estamos añadiendo un nuevo canal actualizamos el listado de urls
        head_nfo, item_tvshow = read_nfo(tvshow_path)
        item_tvshow.channel = "biblioteca"
        item_tvshow.action = "get_temporadas"
        item_tvshow.library_urls[item.channel] = item.url

    # FILTERTOOLS
    # si el canal tiene filtro de idiomas, añadimos el canal y el show
    if episodelist and "list_idiomas" in episodelist[0]:
        # si ya hemos añadido un canal previamente con filtro, añadimos o actualizamos el canal y show
        if "library_filter_show" in item_tvshow:
            item_tvshow.library_filter_show[item.channel] = item.show
        # no habia ningún canal con filtro y lo generamos por primera vez
        else:
            item_tvshow.library_filter_show = {item.channel: item.show}

    if item.channel != "descargas":
        item_tvshow.active = 1  # para que se actualice a diario cuando se llame a library_service

    filetools.write(tvshow_path, head_nfo + item_tvshow.tojson())

    if not episodelist:
        # La lista de episodios esta vacia
        return 0, 0, 0

    # Guardar los episodios
    insertados, sobreescritos, fallidos = save_library_episodes(path, episodelist, item)

    # TODO si fallidos == -1 podriamos comprobar si es necesario eliminar la serie

    return insertados, sobreescritos, fallidos


def save_library_episodes(path, episodelist, serie, silent=False, overwrite=True):
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
    @param overwrite: permite sobreescribir los ficheros existentes
    @type overwrite: bool
    @rtype insertados: int
    @return:  el número de episodios insertados
    @rtype sobreescritos: int
    @return:  el número de episodios sobreescritos
    @rtype fallidos: int
    @return:  el número de episodios fallidos
    """
    logger.info()

    # No hay lista de episodios, no hay nada que guardar
    if not len(episodelist):
        logger.info("No hay lista de episodios, salimos sin crear strm")
        return 0, 0, 0

    insertados = 0
    sobreescritos = 0
    fallidos = 0
    news_in_playcounts = {}

    if overwrite == "everything":
        overwrite = True
        overwrite_everything = True
    else:
        overwrite_everything = False

    # Listamos todos los ficheros de la serie, asi evitamos tener que comprobar si existe uno por uno
    raiz, carpetas_series, ficheros = filetools.walk(path).next()
    ficheros = [filetools.join(path, f) for f in ficheros]

    # Silent es para no mostrar progreso (para library_service)
    if not silent:
        # progress dialog
        p_dialog = platformtools.dialog_progress('streamondemand', 'Aggiunta episodi...')
        p_dialog.update(0, 'Aggiunta episodio...')

    # fix float porque la division se hace mal en python 2.x
    t = float(100) / len(episodelist)

    for i, e in enumerate(episodelist):
        if not silent:
            p_dialog.update(int(math.ceil((i + 1) * t)), 'Aggiunta episodio...', e.title)

        try:
            season_episode = scrapertools.get_season_and_episode(e.title.lower())

            e.infoLabels = serie.infoLabels
            e.contentSeason, e.contentEpisodeNumber = season_episode.split("x")
            season_episode = "%sx%s" % (e.contentSeason, str(e.contentEpisodeNumber).zfill(2))
        except:
            continue

        strm_path = filetools.join(path, "%s.strm" % season_episode)
        nfo_path = filetools.join(path, "%s.nfo" % season_episode)
        json_path = filetools.join(path, ("%s [%s].json" % (season_episode, e.channel)).lower())

        strm_exists = strm_path in ficheros
        nfo_exists = nfo_path in ficheros
        json_exists = json_path in ficheros

        strm_exists_before = True
        nfo_exists_before = True
        json_exists_before = True

        if not strm_exists or overwrite_everything:
            if not overwrite_everything:
                strm_exists_before = False

            # Si no existe season_episode.strm añadirlo
            item_strm = Item(action='play_from_library', channel='biblioteca',
                             strm_path=strm_path.replace(TVSHOWS_PATH, ""), infoLabels={})
            item_strm.contentSeason = e.contentSeason
            item_strm.contentEpisodeNumber = e.contentEpisodeNumber
            item_strm.contentType = e.contentType
            item_strm.contentTitle = season_episode

            # FILTERTOOLS
            if item_strm.list_idiomas:
                # si tvshow.nfo tiene filtro se le pasa al item_strm que se va a generar
                if "library_filter_show" in serie:
                    item_strm.library_filter_show = serie.library_filter_show

                if item_strm.library_filter_show == "":
                    logger.error("Se ha producido un error al obtener el nombre de la serie a filtrar")

            # logger.debug("item_strm" + item_strm.tostring('\n'))
            # logger.debug("serie " + serie.tostring('\n'))
            strm_exists = filetools.write(strm_path, '%s?%s' % (addon_name, item_strm.tourl()))

        item_nfo = None
        if (not nfo_exists or overwrite_everything) and e.infoLabels.get("imdb_id"):
            if not overwrite_everything:
                nfo_exists_before = False

            # Si no existe season_episode.nfo añadirlo
            if e.infoLabels["tmdb_id"]:
                scraper.find_and_set_infoLabels(e)
                head_nfo = "https://www.themoviedb.org/tv/%s/season/%s/episode/%s\n" % (e.infoLabels['tmdb_id'],
                                                                                        e.contentSeason,
                                                                                        e.contentEpisodeNumber)

            elif e.infoLabels["tvdb_id"]:
                head_nfo = e.url_scraper

            else:
                head_nfo = "Aqui ira el xml"  # TODO

            item_nfo = e.clone(channel="biblioteca", url="", action='findvideos',
                               strm_path=strm_path.replace(TVSHOWS_PATH, ""))

            nfo_exists = filetools.write(nfo_path, head_nfo + item_nfo.tojson())

        # Solo si existen season_episode.nfo y season_episode.strm continuamos
        if nfo_exists and strm_exists:

            if not json_exists or overwrite:
                # Obtenemos infoLabel del episodio
                if not item_nfo:
                    head_nfo, item_nfo = read_nfo(nfo_path)

                e.infoLabels = item_nfo.infoLabels

                if filetools.write(json_path, e.tojson()):
                    if not json_exists or overwrite_everything:
                        if not overwrite_everything:
                            json_exists_before = False
                            logger.info("Insertado: %s" % json_path)
                        else:
                            logger.info("Sobreescritos todos los archivos!")
                        # Marcamos episodio como no visto
                        news_in_playcounts[season_episode] = 0
                        # Marcamos la temporada como no vista
                        news_in_playcounts["season %s" % e.contentSeason] = 0
                        # Marcamos la serie como no vista
                        # logger.debug("serie " + serie.tostring('\n'))
                        news_in_playcounts[serie.contentTitle] = 0
                        if (not overwrite_everything and not json_exists):
                            json_exists = True
                    else:
                        logger.info("Sobreescrito: %s" % json_path)
                        sobreescritos += 1
                else:
                    logger.info("Fallido: %s" % json_path)
                    fallidos += 1

        else:
            logger.info("Fallido: %s" % json_path)
            fallidos += 1

        if (not strm_exists_before or not nfo_exists_before or not json_exists_before):
            if (strm_exists and nfo_exists and json_exists):
                insertados += 1
            else:
                logger.error("El archivo strm, nfo o json no existe")

        if not silent and p_dialog.iscanceled():
            break

    if not silent:
        p_dialog.close()

    if news_in_playcounts:
        # Si hay nuevos episodios los marcamos como no vistos en tvshow.nfo ...
        tvshow_path = filetools.join(path, "tvshow.nfo")
        try:
            import datetime
            head_nfo, tvshow_item = read_nfo(tvshow_path)
            tvshow_item.library_playcounts.update(news_in_playcounts)

            if tvshow_item.active == 30:
                tvshow_item.active = 1
            update_last = datetime.date.today()
            tvshow_item.update_last = update_last.strftime('%Y-%m-%d')
            update_next = datetime.date.today() + datetime.timedelta(days=int(tvshow_item.active))
            tvshow_item.update_next = update_next.strftime('%Y-%m-%d')

            filetools.write(tvshow_path, head_nfo + tvshow_item.tojson())
        except:
            logger.error("Error al actualizar tvshow.nfo")
            fallidos = -1

        # ... y actualizamos la biblioteca de Kodi
        if config.is_xbmc() and not silent:
            from platformcode import xbmc_library
            xbmc_library.update(FOLDER_TVSHOWS, filetools.basename(path))

    if fallidos == len(episodelist):
        fallidos = -1

    logger.debug("%s [%s]: insertados= %s, sobreescritos= %s, fallidos= %s" %
                 (serie.contentSerieName, serie.channel, insertados, sobreescritos, fallidos))
    return insertados, sobreescritos, fallidos


def add_pelicula_to_library(item):
    """
        guarda una pelicula en la libreria de cine. La pelicula puede ser un enlace dentro de un canal o un video
        descargado previamente.

        Para añadir episodios descargados en local, el item debe tener exclusivamente:
            - contentTitle: titulo de la pelicula
            - title: titulo a mostrar junto al listado de enlaces -findvideos- ("Reproducir video local HD")
            - infoLabels["tmdb_id"] o infoLabels["imdb_id"]
            - contentType == "movie"
            - channel = "descargas"
            - url : ruta local al video

        @type item: item
        @param item: elemento que se va a guardar.
    """
    logger.info()

    new_item = item.clone(action="findvideos")
    insertados, sobreescritos, fallidos = save_library_movie(new_item)

    if fallidos == 0:
        platformtools.dialog_ok(config.get_localized_string(30131), new_item.contentTitle,
                                config.get_localized_string(30135))  # 'se ha añadido a la biblioteca'
    else:
        platformtools.dialog_ok(config.get_localized_string(30131),
                                "ERRORE, il film non è stato aggiunta alla libreria")


def add_serie_to_library(item, channel=None):
    """
        Guarda contenido en la libreria de series. Este contenido puede ser uno de estos dos:
            - La serie con todos los capitulos incluidos en la lista episodelist.
            - Un solo capitulo descargado previamente en local.

        Para añadir episodios descargados en local, el item debe tener exclusivamente:
            - contentSerieName (o show): Titulo de la serie
            - contentTitle: titulo del episodio para extraer season_and_episode ("1x01 Piloto")
            - title: titulo a mostrar junto al listado de enlaces -findvideos- ("Reproducir video local")
            - infoLabels["tmdb_id"] o infoLabels["imdb_id"]
            - contentType != "movie"
            - channel = "descargas"
            - url : ruta local al video

        @type item: item
        @param item: item que representa la serie a guardar
        @type channel: modulo
        @param channel: canal desde el que se guardara la serie.
            Por defecto se importara item.from_channel o item.channel

    """
    logger.info("show=#" + item.show + "#")
    # logger.debug(item.tostring('\n'))

    if item.channel == "descargas":
        itemlist = [item.clone()]

    else:
        # Esta marca es porque el item tiene algo más aparte en el atributo "extra"
        item.action = item.extra
        if isinstance(item.extra, str) and "###" in item.extra:
            item.action = item.extra.split("###")[0]
            item.extra = item.extra.split("###")[1]

        if item.from_action:
            item.__dict__["action"] = item.__dict__.pop("from_action")
        if item.from_channel:
            item.__dict__["channel"] = item.__dict__.pop("from_channel")

        if not channel:
            try:
                channel = __import__('channels.%s' % item.channel, fromlist=["channels.%s" % item.channel])
            except ImportError:
                exec "import channels." + item.channel + " as channel"

        # Obtiene el listado de episodios
        itemlist = getattr(channel, item.action)(item)

    # Eliminamos de la lista lo q no sean episodios
    for it in itemlist:
        if not scrapertools.get_season_and_episode(it.title):
            itemlist.remove(it)

    if not itemlist:
        platformtools.dialog_ok("Libreria", "ERRORE, la serie non è stata aggiunta alla libreria",
                                "Impossibile ottenere qualsiasi episodio")
        logger.error("La serie %s no se ha podido añadir a la biblioteca. No se ha podido obtener ningun episodio"
                     % item.show)
        return

    insertados, sobreescritos, fallidos = save_library_tvshow(item, itemlist)

    if fallidos == -1:
        platformtools.dialog_ok("Libreria", "ERRORE, la serie non è stata aggiunta alla libreria")
        logger.error("La serie %s no se ha podido añadir a la biblioteca" % item.show)

    elif fallidos > 0:
        platformtools.dialog_ok("Libreria", "ERRORE, la serie non è stata aggiunta completamente alla libreria")
        logger.error("No se han podido añadir %s episodios de la serie %s a la biblioteca" % (fallidos, item.show))
    else:
        platformtools.dialog_ok("Libreria", "La serie è stata aggiunta alla libreria")
        logger.info("[launcher.py] Se han añadido %s episodios de la serie %s a la biblioteca" %
                    (insertados, item.show))
