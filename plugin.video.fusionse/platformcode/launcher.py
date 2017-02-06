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
# XBMC Launcher (xbmc / kodi / boxee)
# ------------------------------------------------------------

import os
import re
import sys
import urllib2

from core import channeltools
from core import config
from core import downloadtools
from core import logger
from core import scrapertools
from core.item import Item
from platformcode import library
from platformcode import platformtools
from platformcode import xbmctools


def start():
    """ Primera funcion que se ejecuta al entrar en el plugin.
    Dentro de esta funcion deberian ir todas las llamadas a las
    funciones que deseamos que se ejecuten nada mas abrir el plugin.
    """
    logger.info("fusionse.platformcode.launcher start")

    # Test if all the required directories are created
    config.verify_directories_created()

def run():
    logger.info("fusionse.platformcode.launcher run")

    # The start() function is not always executed on old platforms (XBMC versions under 12.0)
    if config.OLD_PLATFORM:
        config.verify_directories_created()

    # Extract item from sys.argv
    if sys.argv[2]:
        item = Item().fromurl(sys.argv[2])

    # If no item, this is mainlist
    else:
        item = Item(action="selectchannel", viewmode="movie")

    logger.info("fusionse.platformcode.launcher "+item.tostring())

    # Set server filters
    server_white_list = []
    server_black_list = []
    if config.get_setting('filter_servers') == 'true':
        server_white_list, server_black_list = set_server_list()

    try:

        # If item has no action, stops here
        if item.action == "":
            logger.info("fusionse.platformcode.launcher Item sin accion")
            return

        # Action for main menu in channelselector
        if ( item.action=="selectchannel" ):
            import channelselector
            itemlist = channelselector.getmainlist()

            # Check for updates only on first screen
            if config.get_setting("updatecheck2") == "true":
                logger.info("fusionse.platformcode.launcher Check for plugin updates enabled")
                from core import updater
                
                try:
                    version = updater.checkforupdates()

                    if version:
                        import xbmcgui
                        advertencia = xbmcgui.Dialog()
                        advertencia.ok("Versione "+version+" disponible","E' possibile fare il download della nuova versione\nselezionare la relativa voce nel menu principale")

                        itemlist.insert(0,Item(title="Download versione "+version, version=version, channel="updater", action="update", thumbnail=channelselector.get_thumbnail_path() + "Crystal_Clear_action_info.png"))
                except:
                    import xbmcgui
                    advertencia = xbmcgui.Dialog()
                    advertencia.ok("Impossibile connettersi","Non è stato possibile verificare","aggiornamenti")
                    logger.info("cfusionse.platformcode.launcher Fallo al verificar la actualización")

            else:
                logger.info("fusionse.platformcode.launcher Check for plugin updates disabled")

            xbmctools.renderItems(itemlist, item)

        # Action for updating plugin
        elif (item.action=="update"):

            from core import updater
            updater.update(item)
            if config.get_system_platform()!="xbox":
                import xbmc
                xbmc.executebuiltin( "Container.Refresh" )

        # Action for channel types on channelselector: movies, series, etc.
        elif (item.action=="channeltypes"):
            import channelselector
            itemlist = channelselector.getchanneltypes()

            xbmctools.renderItems(itemlist, item)

        # Action for channel listing on channelselector
        elif (item.action=="listchannels"):
            import channelselector
            itemlist = channelselector.filterchannels(item.category)

            xbmctools.renderItems(itemlist, item)

        # Action in certain channel specified in "action" and "channel" parameters
        else:

            # Entry point for a channel is the "mainlist" action, so here we check parental control
            if item.action=="mainlist":
                
                # Parental control
                can_open_channel = False

                # If it is an adult channel, and user has configured pin, asks for it
                if channeltools.is_adult(item.channel) and config.get_setting("adult_pin")!="":

                    import xbmc
                    keyboard = xbmc.Keyboard("","PIN para canales de adultos",True)
                    keyboard.doModal()

                    if (keyboard.isConfirmed()):
                        tecleado = keyboard.getText()
                        if tecleado==config.get_setting("adult_pin"):
                            can_open_channel = True

                # All the other cases can open the channel
                else:
                    can_open_channel = True

                if not can_open_channel:
                    return

            # Checks if channel exists
            channel_file = os.path.join(config.get_runtime_path(), 'channels', item.channel+".py")
            logger.info("fusionse.platformcode.launcher channel_file=%s" % channel_file)

            if item.channel in ["personal","personal2","personal3","personal4","personal5"]:
                import channels.personal as channel

            elif os.path.exists(channel_file):
                try:
                    channel = __import__('channels.%s' % item.channel, fromlist=["channels.%s" % item.channel])
                except:
                    exec "import channels."+item.channel+" as channel"

            logger.info("fusionse.platformcode.launcher running channel {0} {1}".format(channel.__name__, channel.__file__))

            # Special play action
            if item.action == "play":
                logger.info("fusionse.platformcode.launcher play")

                # First checks if channel has a "play" function
                if hasattr(channel, 'play'):
                    logger.info("fusionse.platformcode.launcher executing channel 'play' method")
                    itemlist = channel.play(item)

                    # Play should return a list of playable URLS
                    if len(itemlist) > 0:
                        item = itemlist[0]
                        xbmctools.play_video(item)
                    
                    # If not, shows user an error message
                    else:
                        import xbmcgui
                        ventana_error = xbmcgui.Dialog()
                        ok = ventana_error.ok("plugin", "No hay nada para reproducir")

                # If player don't have a "play" function, not uses the standard play from xbmctools
                else:
                    logger.info("fusionse.platformcode.launcher executing core 'play' method")
                    xbmctools.play_video(item)

            # Special action for findvideos, where the plugin looks for known urls
            elif item.action == "findvideos":

                if item.strm:
                    # Special action for playing a video from the library
                    play_from_library(item, channel, server_white_list, server_black_list)

                # First checks if channel has a "findvideos" function
                if hasattr(channel, 'findvideos'):
                    itemlist = getattr(channel, item.action)(item)

                # If not, uses the generic findvideos function
                else:
                    logger.info("fusionse.platformcode.launcher no channel 'findvideos' method, "
                                "executing core method")
                    from core import servertools
                    itemlist = servertools.find_video_items(item)
                    if config.get_setting('filter_servers') == 'true':
                        itemlist = filtered_servers(itemlist, server_white_list, server_black_list)


                from platformcode import subtitletools
                subtitletools.saveSubtitleName(item)

                # Show xbmc items as "movies", so plot is visible
                import xbmcplugin

                handle = sys.argv[1]
                xbmcplugin.setContent(int( handle ),"movies")

                # Add everything to XBMC item list
                if type(itemlist) == list and itemlist:
                    xbmctools.renderItems(itemlist, item)

                # If not, it shows an empty list
                # FIXME: Aquí deberíamos mostrar alguna explicación del tipo "No hay elementos, esto pasa por bla bla bla"
                else:
                    xbmctools.renderItems([], item)

            # DrZ3r0
            # Special action for play_from_library, where the plugin looks for known urls
            elif item.action == "play_from_library":
                # Special action for playing a video from the library
                play_from_library(item, channel, server_white_list, server_black_list)

            # Special action for adding a movie to the library
            elif item.action == "add_pelicula_to_library":
                library.add_pelicula_to_library(item)

            # Special action for adding a serie to the library
            elif item.action == "add_serie_to_library":
                library.add_serie_to_library(item, channel)

            # Special action for downloading all episodes from a serie
            elif item.action == "download_all_episodes":
                downloadtools.download_all_episodes(item, channel)

            # Special action for searching, first asks for the words then call the "search" function
            elif item.action=="search":
                logger.info("fusionse.platformcode.launcher search")
                
                import xbmc
                keyboard = xbmc.Keyboard("")
                keyboard.doModal()
                
                if (keyboard.isConfirmed()):
                    tecleado = keyboard.getText()
                    tecleado = tecleado.replace(" ", "+")
                    itemlist = channel.search(item,tecleado)
                else:
                    itemlist = []
                
                xbmctools.renderItems(itemlist, item)

            # For all other actions
            else:
                logger.info("fusionse.platformcode.launcher executing channel '"+item.action+"' method")
                itemlist = getattr(channel, item.action)(item)

                # Activa el modo biblioteca para todos los canales genéricos, para que se vea el argumento
                import xbmcplugin

                handle = sys.argv[1]
                xbmcplugin.setContent(int( handle ),"movies")

                # Añade los items a la lista de XBMC
                if type(itemlist) == list and itemlist:
                    xbmctools.renderItems(itemlist, item)

                # If not, it shows an empty list
                # FIXME: Aquí deberíamos mostrar alguna explicación del tipo "No hay elementos, esto pasa por bla bla bla"
                else:
                    xbmctools.renderItems([], item)

    except urllib2.URLError,e:
        import traceback
        logger.error("fusionse.platformcode.launcher "+traceback.format_exc())

        import xbmcgui
        ventana_error = xbmcgui.Dialog()

        # Grab inner and third party errors
        if hasattr(e, 'reason'):
            logger.info("fusionse.platformcode.launcher Razon del error, codigo: {0}, Razon: {1}".format(e.reason[0], e.reason[1]))
            texto = config.get_localized_string(30050) # "No se puede conectar con el sitio web"
            ok = ventana_error.ok ("plugin", texto)
        
        # Grab server response errors
        elif hasattr(e,'code'):
            logger.info("fusionse.platformcode.launcher codigo de error HTTP : %d" %e.code)
            texto = (config.get_localized_string(30051) % e.code) # "El sitio web no funciona correctamente (error http %d)"
            ok = ventana_error.ok ("plugin", texto)
    
    except:
        import traceback
        import xbmcgui
        logger.error("fusionse.platformcode.launcher "+traceback.format_exc())
        
        patron = 'File "'+os.path.join(config.get_runtime_path(),"channels","").replace("\\","\\\\")+'([^.]+)\.py"'
        canal = scrapertools.find_single_match(traceback.format_exc(),patron)
        
        if canal:
            xbmcgui.Dialog().ok(
                "Errore inaspettato in " + canal,
                "Protrebbe essere un errore di connessione. Il canale web "
                "potrebbe aver modificato la sua struttura oppure si è "
                "verificato un errore in fusionse.\nPer dettagli consulta il log.")
        else:
            xbmcgui.Dialog().ok(
                "Si è verificato un errore su fusionse",
                "Per dettagli consulta il log." )

def set_server_list():
    logger.info("fusionse.platformcode.launcher.set_server_list")

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

def filtered_servers(itemlist, server_white_list, server_black_list):
    logger.info("fusionse.platformcode.launcher.filtered_servers")
    new_list = []
    white_counter = 0
    black_counter = 0

    logger.info("fusionse.platformcode.launcher filtered_servers whiteList %s" % server_white_list)
    logger.info("fusionse.platformcode.launcher filtered_servers blackList %s" % server_black_list)

    if len(server_white_list) > 0:
        logger.info("fusionse.platformcode.launcher filtered_servers whiteList")
        for item in itemlist:
            logger.info("item.title " + item.title)
            if any(server in item.title for server in server_white_list):
                logger.info("found")
                new_list.append(item)
                white_counter += 1
            else:
                logger.info("not found")

    if len(server_black_list) > 0:
        logger.info("fusionse.platformcode.launcher filtered_servers blackList")
        for item in itemlist:
            logger.info("item.title " + item.title)
            if any(server in item.title for server in server_black_list):
                logger.info("found")
                black_counter += 1
            else:
                new_list.append(item)
                logger.info("not found")

    logger.info("fusionse.platformcode.launcher filtered_servers whiteList server %s has #%d rows" %
                (server_white_list, white_counter))
    logger.info("fusionse.platformcode.launcher filtered_servers blackList server %s has #%d rows" %
                (server_black_list, black_counter))

    if len(new_list) == 0:
        new_list = itemlist

    return new_list


def play_from_library(item, channel, server_white_list, server_black_list):
    logger.info("fusionse.platformcode.launcher play_from_library")

    logger.info("fusionse.platformcode.launcher play_from_library item.server=#"+item.server+"#")

    elegido = item
    # DrZ3r0
    if item.action == "findvideos":
        # Ejecuta find_videos, del canal o común
        if hasattr(channel, 'findvideos'):
            itemlist = getattr(channel, item.action)(item)
        else:
            from core import servertools
            itemlist = servertools.find_video_items(item)

            if config.get_setting('filter_servers') == 'true':
                itemlist = filtered_servers(itemlist, server_white_list, server_black_list)

        if len(itemlist) > 0:
            # El usuario elige el mirror
            opciones = []
            for item in itemlist:
                opciones.append(item.title)

            seleccion = platformtools.dialog_select(config.get_localized_string(30163), opciones)
            elegido = itemlist[seleccion]

            if seleccion == -1:
                return

    # Ejecuta el método play del canal, si lo hay
    try:
        itemlist = channel.play(elegido)
        item = itemlist[0]
    except AttributeError:
        item = elegido
    logger.info("fusionse.platformcode.launcher play_from_library Elegido %s (sub %s)" % (item.title,
                                                                                               item.subtitle))

    xbmctools.play_video(item, strmfile=True)
    library.mark_as_watched(item)
