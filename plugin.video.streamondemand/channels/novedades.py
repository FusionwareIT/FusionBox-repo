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
# Channel for recent videos on several channels
#------------------------------------------------------------

import glob
import os
import re
from threading import Thread

from core import channeltools
from core import config
from core import logger
from core.item import Item
from platformcode import platformtools

DEBUG = config.get_setting("debug")
THUMBNAILS = {'0': 'posters', '1': 'banners', '2': 'squares'}

list_newest =[]

def mainlist(item,thumbnail_type="squares"):
    logger.info("streamondemand.channels.novedades mainlist")

    itemlist = []
    list_canales = get_list_canales()

    thumbnail_base = "http://media.tvalacarta.info/pelisalacarta/"+thumbnail_type+"/"
    thumbnail = thumbnail_base + '/disabled'

    if list_canales['peliculas']:
        thumbnail = thumbnail_base + "/thumb_canales_peliculas.png"
    itemlist.append(Item(channel=item.channel, action="novedades", extra="peliculas", title="Películas", thumbnail=thumbnail))

    if list_canales['infantiles']:
        thumbnail = thumbnail_base + "/thumb_canales_infantiles.png"
    itemlist.append(Item(channel=item.channel, action="novedades", extra="infantiles", title="Para niños", thumbnail=thumbnail))

    if list_canales['series']:
        thumbnail = thumbnail_base + "/thumb_canales_series.png"
    itemlist.append(Item(channel=item.channel, action="novedades", extra="series", title="Episodios de series", thumbnail=thumbnail))

    if list_canales['anime']:
        thumbnail = thumbnail_base + "/thumb_canales_anime.png"
    itemlist.append(Item(channel=item.channel, action="novedades", extra="anime", title="Episodios de anime", thumbnail=thumbnail))

    if list_canales['documentales']:
        thumbnail = thumbnail_base + "/thumb_canales_documentales.png"

    itemlist.append(Item(channel=item.channel, action="novedades", extra="documentales", title="Documentales", thumbnail=thumbnail))

    #itemlist.append(Item(channel=item.channel, action="menu_opciones", title="Opciones", viewmode="list",
    #                     thumbnail=thumbnail_base + "/thumb_configuracion.png"))

    return itemlist

def get_list_canales():
    logger.info("streamondemand.channels.novedades get_list_canales")

    list_canales = {'peliculas': [], 'infantiles': [], 'series': [], 'anime': [], 'documentales': []}

    # Rellenar listas de canales disponibles
    channels_path = os.path.join(config.get_runtime_path(), "channels", '*.xml')
    channel_language = config.get_setting("channel_language")

    if channel_language == "":
        channel_language = "all"

    for infile in sorted(glob.glob(channels_path)):
        list_result_canal = []
        channel_name = os.path.basename(infile)[:-4]
        channel_parameters = channeltools.get_channel_parameters(channel_name)

        # No incluir si es un canal inactivo
        if channel_parameters["active"] != "true":
            continue

        # No incluir si es un canal para adultos, y el modo adulto está desactivado
        if channel_parameters["adult"] == "true" and config.get_setting("adult_mode") == "false":
            continue

        # No incluir si el canal es en un idioma filtrado
        if channel_language != "all" and channel_parameters["language"] != channel_language:
            continue

        # Incluir en cada categoria, si en su configuracion el canal esta activado para mostrar novedades
        for categoria in list_canales:
            include_in_newest = config.get_setting("include_in_newest_" + categoria, channel_name)
            if include_in_newest:
                list_canales[categoria].append(channel_name)

    return list_canales


def novedades(item):
    logger.info("streamondemand.channels.novedades item="+item.tostring())

    global list_newest
    l_hilo = []
    list_newest = []

    multithread = config.get_setting("multithread", "novedades")
    logger.info("streamondemand.channels.novedades multithread="+str(multithread))

    list_canales = get_list_canales()

    for channel_name in list_canales[item.extra]:
        logger.info("streamondemand.channels.novedades obteniendo novedades de channel_name="+channel_name)

        # Modo Multi Thread
        if multithread:
            t = Thread(target=get_newest, args=[channel_name, item.extra])
            t.start()
            l_hilo.append(t)

        # Modo single Thread
        else:
            get_newest(channel_name, item.extra)

    # Modo Multi Thread: esperar q todos los hilos terminen
    if multithread:
        for x in l_hilo: x.join()

    result_mode = config.get_setting("result_mode", "novedades")
    if result_mode == 0:  # Agrupados por contenido
        return agruparXcontenido(list_newest, item.extra)
    elif result_mode == 1: # Agrupados por canales
        return agruparXcanal(list_newest, item.extra)
    else: # Sin agrupar
        return noAgrupar(list_newest, item.extra)


def get_newest(channel_name, categoria):
    logger.info("streamondemand.channels.novedades get_newest channel_name="+channel_name+", categoria="+categoria)

    global list_newest

    # Solicitamos las novedades de la categoria (item.extra) buscada en el canal channel
    # Si no existen novedades para esa categoria en el canal devuelve una lista vacia
    try:

        puede = True
        try:
            modulo = __import__('channels.%s' % channel_name, fromlist=["channels.%s" % channel_name])
        except:
            try:
                exec "import channels."+channel_name+" as modulo"
            except:
                puede = False

        if not puede:
            return

        logger.info("pelisalacarta.channels.novedades running channel "+modulo.__name__+" "+modulo.__file__)
        list_result = modulo.newest(categoria)
        logger.info("streamondemand.channels.novedades.get_newest canal= %s %d resultados" %(channel_name, len(list_result)))

        for item in list_result:
            logger.info("streamondemand.channels.novedades.get_newest   item="+item.tostring())
            item.channel = channel_name
            list_newest.append(item)

    except:
        logger.error("No se pueden recuperar novedades de: "+ channel_name)
        import traceback
        logger.error(traceback.format_exc())


def noAgrupar(list_result_canal, categoria):
    itemlist = []

    for i in list_result_canal:
        i.title = re.compile("\[COLO.*?\]",re.DOTALL).sub("",i.title)
        i.title = re.compile("\[/COLO.*?\]",re.DOTALL).sub("",i.title)
        i.title = re.compile("\[B\]",re.DOTALL).sub("",i.title)
        i.title = re.compile("\[/B\]",re.DOTALL).sub("",i.title)
        i.title = i.title + " ["+i.channel+"]"
        itemlist.append(i.clone())

    return sorted(itemlist, key=lambda i:  i.title.lower())


def agruparXcanal(list_result_canal, categoria):
    dict_canales ={}
    itemlist =[]

    for i in list_result_canal:
        if not i.channel in dict_canales:
            dict_canales[i.channel] = []

        # Formatear titulo
        i.title = i.contentTitle
        if (categoria == 'series' or categoria == 'anime') and i.contentEpisodeNumber:
            if not i.contentSeason:
                i.contentSeason = '1'

            try:
                i.title += " - %sx%s" % (i.contentSeason, "{:0>2d}".format(int(i.contentEpisodeNumber)))
            except:
                pass

        # Añadimos el contenido a listado de cada canal
        dict_canales[i.channel].append(i)

    # Añadimos el contenido encontrado en la lista list_result
    for c in sorted(dict_canales):
        itemlist.append(Item(channel="novedades", title=c+':'))
        for i in dict_canales[c]:
            if 'contentCalidad' in i:  i.title += ' (%s)' % i.contentCalidad
            if i.language: i.title += ' [%s]' % i.language
            i.title = '    %s' % i.title

            itemlist.append(i.clone())

    return itemlist


def agruparXcontenido(list_result_canal, categoria):
    dict_contenidos = {}
    list_result = []

    for i in list_result_canal:
        # Formatear titulo
        i.title = i.contentTitle
        if (categoria == 'series' or categoria == 'anime') and i.contentEpisodeNumber:
            if not i.contentSeason:
                i.contentSeason = '1'

            try:
                i.title += " - %sx%s" % (i.contentSeason, "{:0>2d}".format(int(i.contentEpisodeNumber)))
            except:
                pass

        # Eliminar tildes y otros caracteres especiales para la key
        import unicodedata
        try:
            newKey = i.title.lower().strip().decode("UTF-8")
            newKey = ''.join((c for c in unicodedata.normalize('NFD', newKey) if unicodedata.category(c) != 'Mn'))
        except:
            newKey = i.title

        if newKey in dict_contenidos:
            # Si el contenido ya estaba en el diccionario añadirlo a la lista de opciones...
            dict_contenidos[newKey].append(i)
        else:  # ...sino añadirlo al diccionario
            dict_contenidos[newKey] = [i]

    # Añadimos el contenido encontrado en la lista list_result
    for v in dict_contenidos.values():
        title = v[0].title
        if len(v) > 1:
            # Eliminar de la lista de nombres de canales los q esten duplicados
            canales_no_duplicados = []
            for i in v:
                if not i.channel in canales_no_duplicados:
                    canales_no_duplicados.append(i.channel)

            if len(canales_no_duplicados) > 1:
                canales = ', '.join([i for i in canales_no_duplicados[:-1]])
                title += " (En %s y %s)" % (canales, canales_no_duplicados[-1])
            else:
                title += " (En %s)" % (', '.join([i for i in canales_no_duplicados]))

            newItem = v[0].clone(channel="novedades", title=title, action="ver_canales",
                                 sub_list=[i.tourl() for i in v])
        else:
            newItem = v[0].clone(title=title)

        list_result.append(newItem)

    return sorted(list_result, key=lambda i:  i.title.lower())


def ver_canales(item):
    logger.info("streamondemand.channels.novedades ver_canales")
    itemlist = []
    for i in item.sub_list:
        newItem = Item()
        newItem = newItem.fromurl(i)
        logger.debug(newItem.tostring())
        if 'contentCalidad' in newItem:  newItem.title += ' (%s)' % newItem.contentCalidad
        if newItem.language: newItem.title += ' [%s]' % newItem.language
        newItem.title += ' (%s)' % newItem.channel
        itemlist.append(newItem.clone())

    return itemlist


def menu_opciones(item):
    thumbnail_type = config.get_setting("thumbnail_type")
    if not thumbnail_type in THUMBNAILS:
        thumbnail_type = '2'
    preferred_thumbnail = THUMBNAILS[thumbnail_type]

    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Canales incluidos en:",
                         thumbnail="http://media.tvalacarta.info/streamondemand/" + preferred_thumbnail + "/thumb_configuracion.png", folder=False))
    itemlist.append(Item(channel=item.channel, action="settingCanal", extra="peliculas", title="    - Películas ",
                         thumbnail="http://media.tvalacarta.info/streamondemand/" + preferred_thumbnail + "/thumb_canales_peliculas.png", folder=False))
    itemlist.append(Item(channel=item.channel, action="settingCanal", extra="infantiles", title="    - Para niños",
                         thumbnail="http://media.tvalacarta.info/streamondemand/" + preferred_thumbnail + "/thumb_canales_infantiles.png", folder=False))
    itemlist.append(Item(channel=item.channel, action="settingCanal", extra="series", title="    - Episodios de series",
                         thumbnail="http://media.tvalacarta.info/streamondemand/" + preferred_thumbnail + "/thumb_canales_series.png", folder=False))
    itemlist.append(Item(channel=item.channel, action="settingCanal", extra="anime", title="    - Episodios de anime",
                         thumbnail="http://media.tvalacarta.info/streamondemand/" + preferred_thumbnail + "/thumb_canales_anime.png", folder=False))
    itemlist.append(Item(channel=item.channel, action="settingCanal", extra="documentales", title="    - Documentales",
                         thumbnail="http://media.tvalacarta.info/streamondemand/" + preferred_thumbnail + "/thumb_canales_documentales.png", folder=False))
    itemlist.append(Item(channel=item.channel, action="settings", title="Otros ajustes",
                         thumbnail="http://media.tvalacarta.info/streamondemand/"+preferred_thumbnail+"/thumb_configuracion.png", folder=False))
    return itemlist


def settings(item):
    return platformtools.show_channel_settings()


def settingCanal(item):
    channels_path = os.path.join(config.get_runtime_path(), "channels", '*.xml')
    channel_language = config.get_setting("channel_language")

    if channel_language == "":
        channel_language = "all"

    list_controls = []
    for infile in sorted(glob.glob(channels_path)):
        channel_name = os.path.basename(infile)[:-4]
        channel_parameters = channeltools.get_channel_parameters(channel_name)

        # No incluir si es un canal inactivo
        if channel_parameters["active"] != "true":
            continue

        # No incluir si es un canal para adultos, y el modo adulto está desactivado
        if channel_parameters["adult"] == "true" and config.get_setting("adult_mode") == "false":
            continue

        # No incluir si el canal es en un idioma filtrado
        if channel_language != "all" and channel_parameters["language"] != channel_language:
            continue

        # No incluir si en su configuracion el canal no existe 'include_in_newest'
        include_in_newest = config.get_setting("include_in_newest_" + item.extra, channel_name)
        if include_in_newest == "":
            continue

        control = {'id': channel_name,
                      'type': "bool",
                      'label': channel_parameters["title"],
                      'default': include_in_newest,
                      'enabled': True,
                      'visible': True}

        list_controls.append(control)

    return platformtools.show_channel_settings(list_controls=list_controls, callback="save_settings", item=item,
                                               caption= "Canales incluidos en Novedades " + item.title.strip())


def save_settings(item,dict_values):
    for v in dict_values:
        config.set_setting("include_in_newest_" + item.extra, dict_values[v],v)
    #return mainlist(Item())
