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
# XBMC Launcher (xbmc / kodi / boxee)
# ------------------------------------------------------------

import os
import re
import sys
import urllib2

from core import channeltools
from core import config
from core import library
from core import logger
from core import scrapertools
from core.item import Item
from platformcode import platformtools


def start():
    """ Primera funcion que se ejecuta al entrar en el plugin.
    Dentro de esta funcion deberian ir todas las llamadas a las
    funciones que deseamos que se ejecuten nada mas abrir el plugin.
    """
    logger.info("streamondemand.platformcode.launcher start")

    # Test if all the required directories are created
    config.verify_directories_created()

def run():
    logger.info("streamondemand.platformcode.launcher run")

    # Extract item from sys.argv
    if sys.argv[2]:
        item = Item().fromurl(sys.argv[2])

    # If no item, this is mainlist
    else:
        item = Item(channel="channelselector", action="getmainlist", viewmode="movie")

    logger.info("streamondemand.platformcode.launcher "+item.tostring())
    
    try:

        # If item has no action, stops here
        if item.action == "":
            logger.info("streamondemand.platformcode.launcher Item sin accion")
            return

        # Action for main menu in channelselector
        if item.action == "getmainlist":
            import channelselector

            # Check for updates only on first screen
            if config.get_setting("check_for_plugin_updates") == "true":
                logger.info("streamondemand.platformcode.launcher Check for plugin updates enabled")
                from core import updater
                
                try:
                    config.set_setting("plugin_updates_available","0")
                    version = updater.checkforupdates()
                    itemlist = channelselector.getmainlist()

                    if version:
                        config.set_setting("plugin_updates_available","1")

                        platformtools.dialog_ok("Versione "+version+" disponible",
                                                "E' possibile fare il download della nuova versione\n"
                                                "selezionare la relativa voce nel menu principale")

                        itemlist = channelselector.getmainlist()
                        itemlist.insert(0, Item(title="Download versione "+version, version=version, channel="updater",
                                                action="update", thumbnail=channelselector.get_thumb("squares","thumb_actualizar.png")))
                except:
                    import traceback
                    logger.info(traceback.format_exc())
                    platformtools.dialog_ok("Impossibile connettersi", "Non è stato possibile verificare",
                                            "aggiornamenti")
                    logger.info("cpelisalacarta.platformcode.launcher Fallo al verificar la actualización")
                    config.set_setting("plugin_updates_available","0")
                    itemlist = channelselector.getmainlist()

            else:
                logger.info("streamondemand.platformcode.launcher Check for plugin updates disabled")
                config.set_setting("plugin_updates_available","0")
                itemlist = channelselector.getmainlist()

            platformtools.render_items(itemlist, item)

        # Action for updating plugin
        elif item.action == "update":

            from core import updater
            updater.update(item)
            config.set_setting("plugin_updates_available","0")
            if config.get_system_platform() != "xbox":
                import xbmc
                xbmc.executebuiltin("Container.Refresh")

        # Action for channel types on channelselector: movies, series, etc.
        elif item.action == "getchanneltypes":
            import channelselector
            itemlist = channelselector.getchanneltypes()

            platformtools.render_items(itemlist, item)

        # Action for channel listing on channelselector
        elif item.action == "filterchannels":
            import channelselector
            itemlist = channelselector.filterchannels(item.channel_type)

            platformtools.render_items(itemlist, item)

        # Special action for playing a video from the library
        elif item.action == "play_from_library":
            play_from_library(item)
            return

        # Action in certain channel specified in "action" and "channel" parameters
        else:

            # Entry point for a channel is the "mainlist" action, so here we check parental control
            if item.action == "mainlist":
                
                # Parental control
                can_open_channel = False

                # If it is an adult channel, and user has configured pin, asks for it
                if channeltools.is_adult(item.channel) and config.get_setting("adult_pin") != "":

                    tecleado = platformtools.dialog_input("", "PIN per canali per adulti", True)
                    if tecleado is not None:
                        if tecleado == config.get_setting("adult_pin"):
                            can_open_channel = True

                # All the other cases can open the channel
                else:
                    can_open_channel = True

                if not can_open_channel:
                    return

            # Actualiza el canal individual
            if item.action == "mainlist" and item.channel!="channelselector" and config.get_setting("check_for_channel_updates")=="true":
                from core import updater
                updater.update_channel(item.channel)

            # Checks if channel exists
            channel_file = os.path.join(config.get_runtime_path(), 'channels', item.channel+".py")
            logger.info("streamondemand.platformcode.launcher channel_file=%s" % channel_file)

            channel = None

            if item.channel in ["personal", "personal2", "personal3", "personal4", "personal5"]:
                import channels.personal as channel

            elif os.path.exists(channel_file):
                try:
                    channel = __import__('channels.%s' % item.channel, None, None, ["channels.%s" % item.channel])
                except ImportError:
                    exec "import channels."+item.channel+" as channel"

            logger.info("streamondemand.platformcode.launcher running channel "+channel.__name__+" "+channel.__file__)

            # Special play action
            if item.action == "play":
                logger.info("streamondemand.platformcode.launcher play")
                # logger.debug("item_toPlay: " + "\n" + item.tostring('\n'))

                # First checks if channel has a "play" function
                if hasattr(channel, 'play'):
                    logger.info("streamondemand.platformcode.launcher executing channel 'play' method")
                    itemlist = channel.play(item)
                    b_favourite = item.isFavourite
                    # Play should return a list of playable URLS
                    if len(itemlist) > 0:
                        item = itemlist[0]
                        if b_favourite:
                            item.isFavourite = True
                        platformtools.play_video(item)

                    #Permitir varias calidades desde play en el canal
                    elif len(itemlist) > 0 and isinstance(itemlist[0], list):
                        item.video_urls = itemlist
                        platformtools.play_video(item)

                    # If not, shows user an error message
                    else:
                        platformtools.dialog_ok("plugin", "Niente da riprodurre")

                # If player don't have a "play" function, not uses the standard play from platformtools
                else:
                    logger.info("streamondemand.platformcode.launcher executing core 'play' method")
                    platformtools.play_video(item)

            # Special action for findvideos, where the plugin looks for known urls
            elif item.action == "findvideos":

                # First checks if channel has a "findvideos" function
                if hasattr(channel, 'findvideos'):
                    itemlist = getattr(channel, item.action)(item)

                # If not, uses the generic findvideos function
                else:
                    logger.info("streamondemand.platformcode.launcher no channel 'findvideos' method, "
                                "executing core method")
                    from core import servertools
                    itemlist = servertools.find_video_items(item)

                if config.get_setting('filter_servers') == 'true':
                    itemlist = filtered_servers(itemlist)

                from platformcode import subtitletools
                subtitletools.saveSubtitleName(item)

                platformtools.render_items(itemlist, item)

            # Special action for adding a movie to the library
            elif item.action == "add_pelicula_to_library":
                library.add_pelicula_to_library(item)

            # Special action for adding a serie to the library
            elif item.action == "add_serie_to_library":
                library.add_serie_to_library(item, channel)

            # Special action for downloading all episodes from a serie
            elif item.action == "download_all_episodes":
                from channels import descargas
                item.action = item.extra
                del item.extra
                descargas.save_download(item)

            # Special action for searching, first asks for the words then call the "search" function
            elif item.action == "search":
                logger.info("streamondemand.platformcode.launcher search")

                last_search = ""
                last_search_active = config.get_setting("last_search", "buscador")
                if last_search_active:
                    try:
                        current_saved_searches_list = list(config.get_setting("saved_searches_list", "buscador"))
                        last_search = current_saved_searches_list[0]
                    except:
                        pass

                tecleado = platformtools.dialog_input(last_search)
                if tecleado is not None:
                    if last_search_active:
                        from channels import buscador
                        buscador.save_search(tecleado)

                    # TODO revisar 'personal.py' porque no tiene función search y daría problemas
                    # DrZ3r0
                    itemlist = channel.search(item, tecleado.replace(" ", "+"))
                else:
                    itemlist = []
                
                platformtools.render_items(itemlist, item)

            # For all other actions
            else:
                logger.info("streamondemand.platformcode.launcher executing channel '"+item.action+"' method")
                itemlist = getattr(channel, item.action)(item)
                platformtools.render_items(itemlist, item)

    except urllib2.URLError, e:
        import traceback
        logger.error("streamondemand.platformcode.launcher "+traceback.format_exc())

        # Grab inner and third party errors
        if hasattr(e, 'reason'):
            logger.info("streamondemand.platformcode.launcher Razon del error, codigo: "+str(e.reason[0])+", Razon: " +
                        str(e.reason[1]))
            texto = config.get_localized_string(30050)  # "No se puede conectar con el sitio web"
            platformtools.dialog_ok("plugin", texto)

        # Grab server response errors
        elif hasattr(e, 'code'):
            logger.info("streamondemand.platformcode.launcher codigo de error HTTP : %d" % e.code)
            # "El sitio web no funciona correctamente (error http %d)"
            platformtools.dialog_ok("plugin", config.get_localized_string(30051) % e.code)
    
    except:
        import traceback
        logger.error("streamondemand.platformcode.launcher "+traceback.format_exc())
        
        patron = 'File "'+os.path.join(config.get_runtime_path(), "channels", "").replace("\\", "\\\\")+'([^.]+)\.py"'
        canal = scrapertools.find_single_match(traceback.format_exc(), patron)
        
        try:
            import xbmc
            xbmc_version = int(xbmc.getInfoLabel("System.BuildVersion").split(".", 1)[0])
            if xbmc_version > 13:
                log_name = "kodi.log"
            else:
                log_name = "xbmc.log"
            log_message = "Ruta: "+xbmc.translatePath("special://logpath")+log_name
        except:
            log_message = ""

        if canal:
            platformtools.dialog_ok(
                "Errore inaspettato in " + canal,
                "Protrebbe essere un errore di connessione. Il canale web "
                "potrebbe aver modificato la sua struttura oppure si è verificato un errore in streamondemand.",
                "Per dettagli consulta il log.", log_message)
        else:
            platformtools.dialog_ok(
                "Si è verificato un errore su streamondemand",
                "Per dettagli consulta il log.",
                log_message)


def set_server_list():
    logger.info("streamondemand.platformcode.launcher.set_server_list")

    server_white_list = []
    server_black_list = []

    if len(config.get_setting('whitelist')) > 0:
        server_white_list_key = config.get_setting('whitelist').replace(', ', ',').replace(' ,', ',')
        server_white_list = re.split(',', server_white_list_key)

    if len(config.get_setting('blacklist')) > 0:
        server_black_list_key = config.get_setting('blacklist').replace(', ', ',').replace(' ,', ',')
        server_black_list = re.split(',', server_black_list_key)

    logger.info("set_server_list whiteList %s" % server_white_list)
    logger.info("set_server_list blackList %s" % server_black_list)

    return server_white_list, server_black_list


def filtered_servers(itemlist):
    logger.info("streamondemand.platformcode.launcher.filtered_servers")
    new_list = []
    white_counter = 0
    black_counter = 0

    server_white_list, server_black_list = set_server_list()

    if len(server_white_list) > 0:
        # logger.info("streamondemand.platformcode.launcher filtered_servers whiteList")
        for item in itemlist:
            logger.info("item.title " + item.title)
            if any(server in item.title for server in server_white_list):
                # logger.info("found")
                new_list.append(item)
                white_counter += 1
            # else:
            #     logger.info("not found")

    if len(server_black_list) > 0:
        # logger.info("streamondemand.platformcode.launcher filtered_servers blackList")
        for item in itemlist:
            logger.info("item.title " + item.title)
            if any(server in item.title for server in server_black_list):
                # logger.info("found")
                black_counter += 1
            else:
                new_list.append(item)
                # logger.info("not found")

    logger.info("streamondemand.platformcode.launcher filtered_servers whiteList server %s has #%d rows" %
                (server_white_list, white_counter))
    logger.info("streamondemand.platformcode.launcher filtered_servers blackList server %s has #%d rows" %
                (server_black_list, black_counter))

    if len(new_list) == 0:
        new_list = itemlist

    return new_list


def play_from_library(item):
    """
        Los .strm al reproducirlos desde kodi, este espera que sea un archivo "reproducible" asi que no puede contener
        más items, como mucho se puede colocar un dialogo de seleccion.
        Esto lo solucionamos "engañando a kodi" y haciendole creer que se ha reproducido algo, asi despues mediante
        "Container.Update()" cargamos el strm como si un item desde dentro de pelisalacarta se tratara, quitando todas
        las limitaciones y permitiendo reproducir mediante la funcion general sin tener que crear nuevos métodos para
        la biblioteca.
        @type item: item
        @param item: elemento con información
    """
    logger.info("streamondemand.platformcode.launcher play_from_library")
    # logger.debug("item: \n" + item.tostring('\n'))

    import xbmcgui
    import xbmcplugin
    import xbmc
    # Intentamos reproducir una imagen (esto no hace nada y ademas no da error)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True,
                              xbmcgui.ListItem(path=os.path.join(config.get_runtime_path(), "icon.png")))

    # Por si acaso la imagen hiciera (en futuras versiones) le damos a stop para detener la reproduccion
    xbmc.Player().stop()

    # modificamos el action (actualmente la biblioteca necesita "findvideos" ya que es donde se buscan las fuentes
    item.action = "findvideos"

    # y volvemos a lanzar kodi
    if xbmc.getCondVisibility('Window.IsMedia'):
        xbmc.executebuiltin("Container.Update(" + sys.argv[0] + "?" + item.tourl() + ")")

    else:
        from channels import biblioteca
        from platformcode import xbmc_library
        p_dialog = platformtools.dialog_progress_bg('streamondemand', 'Caricamento in corso...')
        p_dialog.update(0, '')

        itemlist = biblioteca.findvideos(item)

        p_dialog.update(50, '')

        if len(itemlist) > 0:
            # El usuario elige el mirror
            opciones = []
            for item in itemlist:
                opciones.append(item.title)

            seleccion = platformtools.dialog_select(config.get_localized_string(30163), opciones)
            if seleccion == -1:
                return

            item = biblioteca.play(itemlist[seleccion])[0]
            p_dialog.update(100, '')

            platformtools.play_video(item)
            p_dialog.close()
            xbmc_library.mark_auto_as_watched(itemlist[seleccion])
