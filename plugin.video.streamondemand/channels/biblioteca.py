# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# Canal para biblioteca de streamondemand
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------

import os

from core import config
from core import filetools
from core import logger
from core import scrapertools
from core.item import Item
from platformcode import library

DEBUG = config.get_setting("debug")


def mainlist(item):
    logger.info("streamondemand.channels.biblioteca mainlist")

    itemlist = list()
    itemlist.append(Item(channel=item.channel, action="peliculas", title="Film"))  #, thumbnail=THUMB_MOVIES))
    itemlist.append(Item(channel=item.channel, action="series", title="Serie"))  #, thumbnail=THUMB_TVSHOWS))

    # itemlist.append(Item(channel=item.channel, title="", thumbnail=None, folder=False))
    # TODO en el caso de que no se puedan usar menus contextuales para configurar datos sobre series o peliculas
    # itemlist.append(Item(channel=item.channel, action="settings", title="Configuración", text_color="gold",
    #                      text_blod=True,
    #                      thumbnail="http://media.tvalacarta.info/pelisalacarta/squares/thumb_configuracion.png"))

    return itemlist


# def settings(item):
#     itemlist = list()
#     itemlist.append(Item(channel=item.channel, action="peliculas", title="Películas"))  #, thumbnail=THUMB_MOVIES))
#     itemlist.append(Item(channel=item.channel, action="settings_series", title="Series"))  #, thumbnail=THUMB_TVSHOWS))
#
#     return itemlist
#
#
# def settings_series(item):
#     logger.info("pelisalacarta.channels.biblioteca settings_series")
#     strm_path = library.TVSHOWS_PATH
#
#     itemlist = []
#
#     # Obtenemos todos los strm de la biblioteca de SERIES recursivamente
#     for raiz, subcarpetas, ficheros in filetools.walk(strm_path):
#         for f in ficheros:
#             if f == "tvshow.json":
#                 i = filetools.join(raiz, f)
#
#                 tvshow = Item().fromjson(filetools.read(i))
#                 logger.debug(tvshow.tostring())
#                 tvshow.contentChannel = tvshow.channel
#                 tvshow.path = os.path.dirname(i)
#                 tvshow.title = os.path.basename(os.path.dirname(i))
#                 tvshow.channel = "biblioteca"
#                 tvshow.action = "conf_series"
#                 tvshow.text_color = ""
#
#                 itemlist.append(tvshow)
#
#     # library.set_infolabels_from_library(itemlist, tipo='TVShows')
#
#     return sorted(itemlist, key=lambda it: it.title.lower())
#
#
# def conf_series(item):
#     logger.info("pelisalacarta.channels.biblioteca settings_series")
#
#     itemlist = []
#     title = "Activar la actualización de episodios" if not item.active else "Desactivar la actualización de episodios"
#
#     itemlist.append(Item(channel=item.channel, action="activar_desactivar", title=title))
#
#     return itemlist
#
#
# def activar_desactivar(item):
#     logger.info("pelisalacarta.channels.biblioteca activar_desactivar")
#
#     logger.info("item .active antes es: {}".format(item.active))
#
#     item.active = not item.active
#     logger.info("item .active despues es: {}".format(item.active))
#
#     return []


def peliculas(item):
    logger.info("streamondemand.channels.biblioteca peliculas")
    strm_path = library.MOVIES_PATH
    download_path = filetools.join(config.get_library_path(), "Descargas", "Cine")

    itemlist = []

    for raiz, subcarpetas, ficheros in filetools.walk(strm_path):
        for f in ficheros:
            if f.endswith(".strm"):
                i = filetools.join(raiz, f)

                movie = Item().fromurl(filetools.read(i))
                movie.contentChannel = movie.channel
                movie.path = i
                movie.title = os.path.splitext(os.path.basename(i))[0].capitalize()
                movie.channel = "biblioteca"
                movie.action = "findvideos"
                movie.text_color = "blue"
                # fix para que no se ejecute el método de play para la biblioteca de Kodi
                movie.strm = False

                itemlist.append(movie)

    # Obtenemos todos los videos de la biblioteca de CINE recursivamente
    for raiz, subcarpetas, ficheros in filetools.walk(download_path):
        for f in ficheros:
            if not f.endswith(".json") and not f.endswith(".nfo")and not f.endswith(".srt"):
                i = filetools.join(raiz, f)

                movie = Item()
                movie.contentChannel = "local"
                movie.path = i
                movie.title = os.path.splitext(os.path.basename(i))[0].capitalize()
                movie.channel = "biblioteca"
                movie.action = "play"
                movie.text_color = "green"

                itemlist.append(movie)

    library.set_infolabels_from_library(itemlist, tipo='Movies')

    # Agrupamos las peliculas por canales
    join_itemlist = []

    for i in range(len(itemlist)):
        encontrado = False
        for j in range(i + 1, len(itemlist)):
            if "tmdb_id" in itemlist[i].infoLabels and "tmdb_id" in itemlist[j].infoLabels:
                if itemlist[i].infoLabels["tmdb_id"] == itemlist[j].infoLabels["tmdb_id"]:
                    encontrado = True

                    if "list_channels" not in itemlist[i]:
                        list_channels = []
                        dict_first_channel = {"path": itemlist[i].path, "channel": itemlist[i].contentChannel}
                        list_channels.append(dict_first_channel.copy())
                        itemlist[j].list_channels = list_channels

                    dict_other_channel = {"path": itemlist[j].path, "channel": itemlist[j].contentChannel}
                    itemlist[j].list_channels.append(dict_other_channel.copy())
                    itemlist[j].action = "get_canales_movies"
                    itemlist[j].text_color = "orange"

        # TODO pendiente de probar
        if "contentTitle" in itemlist[i] and itemlist[i].contentTitle != "":
            itemlist[i].title = itemlist[i].contentTitle

        if not encontrado:
            join_itemlist.append(itemlist[i])

    return sorted(join_itemlist, key=lambda it: it.title.lower())


def get_canales_movies(item):
    logger.info("streamondemand.channels.biblioteca get_canales_movies")
    itemlist = []
    # Recorremos el diccionario de canales
    for channel in item.list_channels:
        if channel["channel"] == "local":
            title = '{0} [{1}]'.format(item.contentTitle, channel["channel"])
            itemlist.append(item.clone(action='play', channel="biblioteca", title=title, path=channel['path'],
                                       contentTitle=item.title, contentChannel=channel["channel"], text_color=""))
        else:
            title = '{0} [{1}]'.format(item.contentTitle, channel["channel"])
            itemlist.append(item.clone(action='findvideos', title=title, path=channel['path'],
                                       contentChannel=channel["channel"], text_color=""))

    return sorted(itemlist, key=lambda it: it.contentChannel.lower() if not it.contentChannel == "local" else 0)


def series(item):
    logger.info("streamondemand.channels.biblioteca series")
    strm_path = library.TVSHOWS_PATH
    download_path = filetools.join(config.get_library_path(), "Descargas", "Series")
    itemlist = []

    # Obtenemos todos los strm de la biblioteca de SERIES recursivamente
    for raiz, subcarpetas, ficheros in filetools.walk(strm_path):
        for f in ficheros:
            if f == "tvshow.json":
                i = filetools.join(raiz, f)

                tvshow = Item().fromjson(filetools.read(i))
                logger.debug(tvshow.tostring())
                tvshow.contentChannel = tvshow.channel
                tvshow.path = os.path.dirname(i)
                tvshow.title = os.path.basename(os.path.dirname(i))
                tvshow.channel = "biblioteca"
                tvshow.action = "get_temporadas"
                tvshow.text_color = "blue"

                itemlist.append(tvshow)

    # Obtenemos todos los videos de la biblioteca de SERIES recursivamente
    for raiz, subcarpetas, ficheros in filetools.walk(download_path):
        for f in ficheros:
            if f == "tvshow.json":
                i = filetools.join(raiz, f)

                tvshow = Item().fromjson(filetools.read(i))
                tvshow.contentChannel = "local"
                tvshow.path = os.path.dirname(i)
                tvshow.title = os.path.basename(os.path.dirname(i))
                tvshow.channel = "biblioteca"
                tvshow.action = "get_temporadas"
                tvshow.text_color = "green"

                itemlist.append(tvshow)

    library.set_infolabels_from_library(itemlist, tipo='TVShows')

    # Agrupamos las series por canales
    join_itemlist = []

    for i in range(len(itemlist)):
        encontrado = False
        for j in range(i + 1, len(itemlist)):
            if "tmdb_id" in itemlist[i].infoLabels and "tmdb_id" in itemlist[j].infoLabels:
                if itemlist[i].infoLabels["tmdb_id"] == itemlist[j].infoLabels["tmdb_id"]:
                    encontrado = True

                    if "list_channels" not in itemlist[i]:
                        list_channels = []
                        dict_first_channel = {"path": itemlist[i].path, "channel": itemlist[i].contentChannel}
                        list_channels.append(dict_first_channel.copy())
                        itemlist[j].list_channels = list_channels

                    dict_other_channel = {"path": itemlist[j].path, "channel": itemlist[j].contentChannel}
                    itemlist[j].list_channels.append(dict_other_channel.copy())
                    itemlist[j].action = "get_canales_tvshow"
                    itemlist[j].text_color = "orange"

        if "contentTitle" in itemlist[i] and itemlist[i].contentTitle != "":
            itemlist[i].title = itemlist[i].contentTitle

        if not encontrado:
            join_itemlist.append(itemlist[i])

    return sorted(join_itemlist, key=lambda it: it.title.lower())


def get_canales_tvshow(item):
    logger.info("streamondemand.channels.biblioteca get_canales_tvshow")
    logger.debug(item.tostring())
    itemlist = []

    # Recorremos el listado de canales
    for channel in item.list_channels:
        title = '{0} [{1}]'.format(item.contentTitle, channel["channel"])
        itemlist.append(item.clone(action='get_temporadas', title=title, path=channel['path'],
                                   contentChannel=channel["channel"], text_color=""))

    return sorted(itemlist, key=lambda it: it.contentChannel.lower() if not it.contentChannel == "local" else 0)


def get_temporadas(item):
    logger.info("streamondemand.channels.biblioteca get_temporadas")
    itemlist = []
    dict_temp = {}

    raiz, carpetas_series, ficheros = filetools.walk(item.path).next()

    if config.get_setting("no_pile_on_seasons") == "Siempre":
        return get_episodios(item)

    for i in ficheros:
        if "tvshow" not in i:
            season = i.split('x')[0]
            dict_temp[season] = "Stagione " + str(season)

    if config.get_setting("no_pile_on_seasons") == "Solo se presente una stagione" and len(dict_temp) == 1:
        return get_episodios(item)
    else:
        # Creamos un item por cada temporada
        for season, title in dict_temp.items():
            # fix para que se filtren bien los contenido, ya que sino se hereda el campo
            item.infoLabels['season'] = ""
            new_item = item.clone(action="get_episodios", title=title, contentTitle=title, contentSeason=season,
                                  contentEpisodeNumber="", filtrar_season=True, text_color="")
            itemlist.append(new_item)
            # logger.debug(new_item.tostring())

        if len(itemlist) > 1:
            itemlist = sorted(itemlist, key=lambda it: int(it.contentSeason))

        if config.get_setting("show_all_seasons") == "true":
            new_item = item.clone(action="get_episodios", title="*Tutte le stagioni", text_color="")
            itemlist.insert(0, new_item)

    return itemlist


def get_episodios(item):
    logger.info("streamondemand.channels.biblioteca get_episodios")
    itemlist = []
    
    # Obtenemos los archivos de los episodios
    raiz, carpetas_series, ficheros = filetools.walk(item.path).next()

    # Crear un item en la lista para cada strm encontrado
    for i in ficheros:
        # strm
        if i.endswith(".strm"):
            season, episode = scrapertools.get_season_and_episode(i).split("x")
            # Si hay q filtrar por temporada, ignoramos los capitulos de otras temporadas
            if item.filtrar_season and int(season) != int(item.contentSeason):
                continue

            epi = Item().fromurl(filetools.read(filetools.join(raiz, i)))
            epi.contentChannel = item.contentChannel
            epi.path = filetools.join(raiz, i)
            epi.title = i
            epi.channel = "biblioteca"
            epi.action = "findvideos"
            epi.contentEpisodeNumber = episode
            epi.contentSeason = season
            # fix sobreescribe el color del texto si viene pasado en el strm
            epi.text_color = ""
            # fix para que no se ejecute el método de play para la biblioteca de Kodi
            epi.strm = False

            itemlist.append(epi)

        # videos
        elif not i.endswith(".nfo") and not i.endswith(".json") and not i.endswith(".srt"):
            season, episode = scrapertools.get_season_and_episode(i).split("x")
            # Si hay q filtrar por temporada, ignoramos los capitulos de otras temporadas
            if item.filtrar_season and int(season) != int(item.contentSeason):
                continue

            epi = Item()
            epi.contentChannel = "local"
            epi.path = filetools.join(raiz, i)
            epi.title = i
            epi.channel = "biblioteca"
            epi.action = "play"
            epi.contentEpisodeNumber = episode
            epi.contentSeason = season

            itemlist.append(epi)

    library.set_infolabels_from_library(itemlist, tipo="Episodes")
    return sorted(itemlist, key=get_sort_temp_epi)


def get_sort_temp_epi(item):
    # logger.debug(item.tostring())
    if item.infoLabels and item.infoLabels.get('season', "1") != "" and item.infoLabels.get('episode', "1") != "":
        return int(item.infoLabels.get('season', "1")), int(item.infoLabels.get('episode', "1"))
    else:
        temporada, capitulo = scrapertools.get_season_and_episode(item.title.lower()).split('x')
        return int(temporada), int(capitulo)


def findvideos(item):
    logger.info("streamondemand.channels.biblioteca findvideos")
    canal = item.contentChannel

    channel = __import__('channels.%s' % item.contentChannel, fromlist=["channels.%s" % item.contentChannel])
    if hasattr(channel, "findvideos"):
        new_item = item.clone(channel=item.contentChannel)
        itemlist = getattr(channel, "findvideos")(new_item)
    else:
        from core import servertools
        itemlist = servertools.find_video_items(item)

    for v in itemlist:
        if v.action == "play":
            v.infoLabels = item.infoLabels
            v.contentTitle = item.contentTitle
            v.contentChannel = canal
            v.channel = "biblioteca"
            v.path = item.path

    return itemlist


def play(item):
    logger.info("streamondemand.channels.biblioteca play")

    if not item.contentChannel == "local":
        channel = __import__('channels.%s' % item.contentChannel, fromlist=["channels.%s" % item.contentChannel])
        if hasattr(channel, "play"):
            itemlist = getattr(channel, "play")(item)
        else:
            itemlist = [item.clone()]
    else:
        itemlist = [item.clone(url=item.path, server="local")]

    library.mark_as_watched(item)

    for v in itemlist:
        v.infoLabels = item.infoLabels
        v.title = item.contentTitle
        v.thumbnail = item.thumbnail
        v.contentThumbnail = item.thumbnail

    return itemlist

