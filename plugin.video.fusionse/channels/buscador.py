# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# fusionse - XBMC Plugin
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------
import Queue
import glob
import os
import re
import time
import urllib
from threading import Thread

from core import channeltools
from core import config
from core import logger
from core.item import Item
from lib.fuzzywuzzy import fuzz
from platformcode import platformtools

logger.info("fusionse.channels.buscador init")

DEBUG = config.get_setting("debug")

TIMEOUT_TOTAL = 75


def mainlist(item, preferred_thumbnail="squares"):
    logger.info("fusionse.channels.buscador mainlist")

    itemlist = [
        Item(channel=item.channel,
             action="search",
             extra="movie",
             thumbnail="http://i.imgur.com/pE5WSZp.png",
             title="[COLOR yellow]Nuova ricerca film...[/COLOR]"),
        Item(channel=item.channel,
             action="search",
             extra="serie",
             thumbnail="http://i.imgur.com/pE5WSZp.png",
             title="[COLOR yellow]Nuova ricerca serie tv...[/COLOR]"),
        Item(channel=item.channel,
             thumbnail="http://i.imgur.com/pE5WSZp.png",
             action="settings",
             title="[COLOR green]Altre impostazioni[/COLOR]")
    ]

    saved_searches_list = get_saved_searches()

    for saved_search_text in saved_searches_list:
        itemlist.append(
            Item(channel=item.channel, action="do_search", title=' "' + saved_search_text.split('{}')[0] + '"',
                 extra=saved_search_text))

    if len(saved_searches_list) > 0:
        itemlist.append(
            Item(channel=item.channel,
                 action="clear_saved_searches",
                 thumbnail="http://i.imgur.com/pE5WSZp.png",
                 title="[COLOR red]Elimina cronologia ricerche[/COLOR]"))

    return itemlist


def opciones(item):
    itemlist = [Item(channel=item.channel, action="settingCanal", title="Scegli i canali da includere nella ricerca"),
                Item(channel=item.channel, action="clear_saved_searches", title="Cancella ricerche salvate"),
                Item(channel=item.channel, action="settings", title="Altre opzioni")]
    return itemlist


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

        # No incluir si en la configuracion del canal no existe "include_in_global_search"
        include_in_global_search = config.get_setting("include_in_global_search", channel_name)
        if include_in_global_search == "":
            continue

        control = {'id': channel_name,
                   'type': "bool",
                   'label': channel_parameters["title"],
                   'default': include_in_global_search,
                   'enabled': True,
                   'visible': True}

        list_controls.append(control)

    return platformtools.show_channel_settings(list_controls=list_controls,
                                               caption="Canali inclusi nella ricerca globale",
                                               callback="save_settings", item=item)


def save_settings(item, dict_values):
    for v in dict_values:
        config.set_setting("include_in_global_search", dict_values[v], v)


def settings(item):
    return platformtools.show_channel_settings()


def search(item, tecleado):
    logger.info("fusionse.channels.buscador search")

    item.extra = tecleado + '{}' + item.extra

    if tecleado != "":
        save_search(item.extra)

    return do_search(item)


def channel_search(queue, channel_parameters, category, tecleado):
    try:
        search_results = []

        title_search = urllib.unquote_plus(tecleado)

        exec "from channels import " + channel_parameters["channel"] + " as module"
        mainlist = module.mainlist(Item(channel=channel_parameters["channel"]))

        for item in mainlist:
            if item.action != "search" or category and item.extra != category:
                continue

            for res_item in module.search(item.clone(), tecleado):
                title = res_item.fulltitle

                # Clean up a bit the returned title to improve the fuzzy matching
                title = re.sub(r'\(.*\)', '', title)  # Anything within ()
                title = re.sub(r'\[.*\]', '', title)  # Anything within []

                # Check if the found title fuzzy matches the searched one
                if fuzz.WRatio(title_search, title) > 85:
                    res_item.title = "[COLOR azure]" + res_item.title + "[/COLOR][COLOR orange] su [/COLOR][COLOR green]" + channel_parameters["title"] + "[/COLOR]"
                    search_results.append(res_item)

        queue.put(search_results)

    except:
        logger.error("No se puede buscar en: " + channel_parameters["title"])
        import traceback
        logger.error(traceback.format_exc())


# Esta es la función que realmente realiza la búsqueda
def do_search(item):
    logger.info("fusionse.channels.buscador do_search")

    tecleado, category = item.extra.split('{}')

    itemlist = []

    channels_path = os.path.join(config.get_runtime_path(), "channels", '*.xml')
    logger.info("fusionse.channels.buscador channels_path=" + channels_path)

    channel_language = config.get_setting("channel_language")
    logger.info("fusionse.channels.buscador channel_language=" + channel_language)
    if channel_language == "":
        channel_language = "all"
        logger.info("fusionse.channels.buscador channel_language=" + channel_language)

    progreso = platformtools.dialog_progress_bg("Cercando " + tecleado, "")
    channel_files = glob.glob(channels_path)

    number_of_channels = 0
    search_results = Queue.Queue()

    for infile in channel_files:

        basename_without_extension = os.path.basename(infile)[:-4]

        channel_parameters = channeltools.get_channel_parameters(basename_without_extension)

        # No busca si es un canal inactivo
        if channel_parameters["active"] != "true":
            continue

        # En caso de busqueda por categorias
        if category and category not in channel_parameters["categories"]:
            continue

        # No busca si es un canal para adultos, y el modo adulto está desactivado
        if channel_parameters["adult"] == "true" and config.get_setting("adult_mode") == "false":
            continue

        # No busca si el canal es en un idioma filtrado
        if channel_language != "all" and channel_parameters["language"] != channel_language:
            continue

        # No busca si es un canal excluido de la busqueda global
        include_in_global_search = channel_parameters["include_in_global_search"]
        if include_in_global_search == "":
            # Buscar en la configuracion del canal
            include_in_global_search = str(config.get_setting("include_in_global_search", basename_without_extension))
        if include_in_global_search.lower() != "true":
            continue

        t = Thread(target=channel_search, args=[search_results, channel_parameters, category, tecleado])
        t.setDaemon(True)
        t.start()
        number_of_channels += 1

    start_time = int(time.time())

    completed_channels = 0
    while completed_channels < number_of_channels:

        delta_time = int(time.time()) - start_time
        if len(itemlist) <= 0:
            timeout = None  # No result so far,lets the thread to continue working until a result is returned
        elif delta_time >= TIMEOUT_TOTAL:
            break  # At least a result matching the searched title has been found, lets stop the search
        else:
            timeout = TIMEOUT_TOTAL - delta_time  # Still time to gather other results

        progreso.update(completed_channels * 100 / number_of_channels)

        try:
            itemlist.extend(search_results.get(timeout=timeout))
            completed_channels += 1
        except:
            # Expired timeout raise an exception
            break

    progreso.close()

    itemlist = sorted(itemlist, key=lambda item: item.fulltitle)

    return itemlist


def save_search(text):
    saved_searches_limit = int((10, 20, 30, 40,)[int(config.get_setting("saved_searches_limit", "buscador"))])

    saved_searches_list = list(config.get_setting("saved_searches_list", "buscador"))

    if text in saved_searches_list:
        saved_searches_list.remove(text)

    saved_searches_list.insert(0, text)

    config.set_setting("saved_searches_list", saved_searches_list[:saved_searches_limit], "buscador")


def clear_saved_searches(item):
    config.set_setting("saved_searches_list", list(), "buscador")
    platformtools.dialog_ok("Ricerca", "Ricerche cancellate correttamente")


def get_saved_searches():
    return list(config.get_setting("saved_searches_list", "buscador"))
