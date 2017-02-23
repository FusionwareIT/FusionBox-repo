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
# Configuración
# ------------------------------------------------------------

import os

from core import config
from core import filetools
from core import logger
from core.item import Item

DEBUG = True
CHANNELNAME = "configuracion"


def mainlist(item):
    logger.info()

    itemlist = list()
    itemlist.append(Item(channel=CHANNELNAME, title="Preferenze", action="settings", folder=False,
                         thumbnail=get_thumbnail_path("thumb_configuracion.png")))

    itemlist.append(Item(channel=CHANNELNAME, title="", action="", folder=False,
                         thumbnail=get_thumbnail_path("thumb_configuracion.png")))

    itemlist.append(Item(channel=CHANNELNAME, title="Impostazioni speciali", action="", folder=False,
                         thumbnail=get_thumbnail_path("thumb_configuracion.png")))
    itemlist.append(Item(channel="novedades", title="   Impostazioni 'Novità'", action="menu_opciones",
                         folder=True, thumbnail=get_thumbnail_path("thumb_novedades.png")))
    itemlist.append(Item(channel="buscador",  title="   Impostazioni della ricerca globale", action="opciones", folder=True,
                         thumbnail=get_thumbnail_path("thumb_buscar.png")))

    if config.get_library_support():
        itemlist.append(Item(channel="biblioteca", title="   Impostazioni libreria",
                             action="channel_config", folder=True,
                             thumbnail=get_thumbnail_path("thumb_biblioteca.png")))
        itemlist.append(Item(channel="biblioteca", action="update_biblio", folder=False,
                             thumbnail=get_thumbnail_path("thumb_biblioteca.png"),
                             title="   Recupera nuovi episodi e aggiorna la libreria"))

    itemlist.append(Item(channel=CHANNELNAME, title="Avvia aggiornamenti", action="check_for_updates", folder=False))

    itemlist.append(Item(channel=item.channel, action="", title="", folder=False,
                         thumbnail=get_thumbnail_path("thumb_configuracion.png")))

    itemlist.append(Item(channel=CHANNELNAME, title="Impostazioni canali", action="", folder=False,
                         thumbnail=get_thumbnail_path("thumb_configuracion.png")))

    import channelselector
    from core import channeltools
    channel_list = channelselector.filterchannels("all")

    for channel in channel_list:
        try:
          jsonchannel = channeltools.get_channel_json(channel.channel)
        except:
          continue
        if jsonchannel.get("settings"):
            setting = jsonchannel["settings"]
            if type(setting) == list:
                if len([s for s in setting if "id" in s and "include_in_" not in s["id"]]):
                    active_status = None
                    if config.get_setting("enabled", channel.channel):
                        active_status = config.get_setting("enabled", channel.channel)
                    else:
                        channel_parameters = channeltools.get_channel_parameters(channel.channel)
                        active_status = channel_parameters['active']

                    if active_status == "true":
                        itemlist.append(Item(channel=CHANNELNAME,
                                             title="   Configurazione canale '%s'" % channel.title,
                                             action="channel_config", config=channel.channel,
                                             folder=False,
                                             thumbnail=channel.thumbnail))

    return itemlist


def check_for_updates(item):
    from core import updater

    try:
        version = updater.checkforupdates()
        if version:
            import xbmcgui
            yes_pressed = xbmcgui.Dialog().yesno( "Versione "+version+" disponible" , "Installarla?" )
      
            if yes_pressed:
                item = Item(version=version)
                updater.update(item)

    except:
        pass


def channel_config(item):
    from platformcode import platformtools
    return platformtools.show_channel_settings(channelpath=filetools.join(config.get_runtime_path(), "channels",
                                                                          item.config))

def get_all_versions(item):
    logger.info()

    itemlist = []

    # Lee la versión local
    from core import updater

    # Descarga la lista de versiones
    from core import api
    api_response = api.plugins_get_all_packages()

    if api_response["error"]:
        from platformcode import platformtools
        platformtools.dialog_ok("Errore", "C'è stato un errore scaricando l'elenco delle versioni")
        return

    for entry in api_response["body"]:

        if entry["package"]=="plugin":
            title = "streamondemand "+entry["tag"]+" (Publicada "+entry["date"]+")"
            local_version_number = updater.get_current_plugin_version()
        elif entry["package"]=="channels":
            title = "Canales (Publicada "+entry["date"]+")"
            local_version_number = updater.get_current_channels_version()
        elif entry["package"]=="servers":
            title = "Servidores (Publicada "+entry["date"]+")"
            local_version_number = updater.get_current_servers_version()
        else:
            title = entry["package"]+" (Publicada "+entry["date"]+")"
            local_version_number = None

        if local_version_number is None:
            title = title

        elif entry["version"] == local_version_number:
            title = title + " ACTUAL"

        elif entry["version"] > local_version_number:
            title = "[COLOR yellow]"+ title + " ¡NUEVA VERSIÓN![/COLOR]"

        else:
            title = "[COLOR FF666666]"+ title + "[/COLOR]"

        itemlist.append(Item(channel=CHANNELNAME, title=title, url=entry["url"], filename=entry["filename"], package=entry["package"], version=str(entry["version"]), action="download_and_install_package", folder=False))

    return itemlist

def download_and_install_package(item):
    logger.info()

    from core import updater
    from platformcode import platformtools

    if item.package=="plugin":
        if int(item.version)<updater.get_current_plugin_version():
            if not platformtools.dialog_yesno("Installazione versione precedente","Sei sicuro di voler installare una versione precedente?"):
                return
        elif int(item.version)==updater.get_current_plugin_version():
            if not platformtools.dialog_yesno("Reinstallare versione attuale","Sei sicuro di voler reinstallare la stessa versione già presente?"):
                return
        elif int(item.version)>updater.get_current_plugin_version():
            if not platformtools.dialog_yesno("Installazione nuova versione","Sei sicuro di voler installare questa nuova versione?"):
                return
    else:
        if not platformtools.dialog_yesno("Pacchetto di installazione","Sei sicuro di voler installare questo pacchetto?"):
            return

    local_file_name = os.path.join( config.get_data_path() , item.filename)
    updater.download_and_install(item.url,local_file_name)

    if item.package=="channels":
        updater.set_current_channels_version(item.version)
    elif item.package=="servers":
        updater.set_current_servers_version(item.version)
    elif item.package=="plugin":
        updater.set_current_plugin_version(item.version)

    if config.is_xbmc() and config.get_system_platform() != "xbox":
        import xbmc
        xbmc.executebuiltin("Container.Refresh")

def settings(item):
    config.open_settings()


def menu_addchannels(item):
    logger.info()
    itemlist = list()
    itemlist.append(Item(channel=CHANNELNAME, title="# Copia de seguridad automática en caso de sobrescritura",
                         action="", text_color="green"))
    itemlist.append(Item(channel=CHANNELNAME, title="Añadir o actualizar canal", action="addchannel", folder=False))
    itemlist.append(Item(channel=CHANNELNAME, title="Añadir o actualizar conector", action="addchannel", folder=False))
    itemlist.append(Item(channel=CHANNELNAME, title="Mostrar ruta de carpeta para copias de seguridad",
                         action="backups", folder=False))
    itemlist.append(Item(channel=CHANNELNAME, title="Eliminar copias de seguridad guardadas", action="backups",
                         folder=False))

    return itemlist


def addchannel(item):
    from platformcode import platformtools
    import os
    import time
    logger.info()
    
    tecleado = platformtools.dialog_input("", "Inserire l'URL")
    if not tecleado:
        return
    logger.info("url=%s" % tecleado)

    local_folder = config.get_runtime_path()
    if "canal" in item.title:
        local_folder = filetools.join(local_folder, 'channels')
        folder_to_extract = "channels"
        info_accion = "canal"
    else:
        local_folder = filetools.join(local_folder, 'servers')
        folder_to_extract = "servers"
        info_accion = "conector"

    # Detecta si es un enlace a un .py o .xml (pensado sobre todo para enlaces de github)
    try:
        extension = tecleado.rsplit(".", 1)[1]
    except:
        extension = ""

    files = []
    zip = False
    if extension == "py" or extension == "xml":
        filename = tecleado.rsplit("/", 1)[1]
        localfilename = filetools.join(local_folder, filename)
        files.append([tecleado, localfilename, filename])
    else:
        import re
        from core import scrapertools
        # Comprueba si la url apunta a una carpeta completa (channels o servers) de github
        if re.search(r'https://github.com/[^\s]+/'+folder_to_extract, tecleado):
            try:
                data = scrapertools.downloadpage(tecleado)
                matches = scrapertools.find_multiple_matches(data,
                                                             '<td class="content">.*?href="([^"]+)".*?title="([^"]+)"')
                for url, filename in matches:
                    url = "https://raw.githubusercontent.com" + url.replace("/blob/", "/")
                    localfilename = filetools.join(local_folder, filename)
                    files.append([url, localfilename, filename])
            except:
                import traceback
                logger.info("Detalle del error: %s" % traceback.format_exc())
                platformtools.dialog_ok("Errore", "L'URL non è corretto o non disponibile")
                return
        else:
            filename = 'new%s.zip' % info_accion
            localfilename = filetools.join(config.get_data_path(), filename)
            files.append([tecleado, localfilename, filename])
            zip = True

    logger.info("localfilename=%s" % localfilename)
    logger.info("descarga fichero...")
    
    try:
        if len(files) > 1:
            lista_opciones = ["No", "Si", "Si (Sovrascrivere tutto)"]
            overwrite_all = False
        from core import downloadtools
        for url, localfilename, filename in files:
            result = downloadtools.downloadfile(url, localfilename, continuar=False)
            if result == -3:
                if len(files) == 1:
                    dyesno = platformtools.dialog_yesno("Il file esiste già", "%s %s esiste già. "
                                                                                "Vuoi sovrascrivere?" %
                                                        (info_accion, filename))
                else:
                    if not overwrite_all:
                        dyesno = platformtools.dialog_select("Il file %s esiste già, vuoi sovrascrivere?"
                                                             % filename, lista_opciones)
                    else:
                        dyesno = 1
                # Diálogo cancelado
                if dyesno == -1:
                    return
                # Caso de carpeta github, opción sobrescribir todos
                elif dyesno == 2:
                    overwrite_all = True
                elif dyesno:
                    hora_folder = "Backup [%s]" % time.strftime("%d-%m_%H-%M", time.localtime())
                    backup = filetools.join(config.get_data_path(), 'backups', hora_folder, folder_to_extract)
                    if not filetools.exists(backup):
                        os.makedirs(backup)
                    import shutil
                    shutil.copy2(localfilename, filetools.join(backup, filename))
                    downloadtools.downloadfile(url, localfilename, continuar=True)
                else:
                    if len(files) == 1:
                        return
                    else:
                        continue
    except:
        import traceback
        logger.info("Detalle del error: %s" % traceback.format_exc())
        return

    if zip:
        try:
            # Lo descomprime
            logger.info("descomprime fichero...")
            from core import ziptools
            unzipper = ziptools.ziptools()
            logger.info("destpathname=%s" % local_folder)
            unzipper.extract(localfilename, local_folder, folder_to_extract, True, True)
        except:
            import traceback
            logger.error("Detalle del error: %s" % traceback.format_exc())
            # Borra el zip descargado
            filetools.remove(localfilename)
            platformtools.dialog_ok("Errore", "C'è stato un errore nell'estrazione del file")
            return

        # Borra el zip descargado
        logger.info("borra fichero...")
        filetools.remove(localfilename)
        logger.info("...fichero borrado")

    platformtools.dialog_ok("Successo", "Aggiornamento/installazione eseguita correttamente")


def backups(item):
    from platformcode import platformtools
    logger.info()

    ruta = filetools.join(config.get_data_path(), 'backups')
    ruta_split = ""
    if "ruta" in item.title:
        heading = "Ruta de copias de seguridad"
        if not filetools.exists(ruta):
            folders = "Carpeta no creada"
        else:
            folders = str(len(filetools.listdir(ruta))) + " copia/s de seguridad guardadas"
        if len(ruta) > 55:
            ruta_split = ruta[55:]
            ruta = ruta[:55]
        platformtools.dialog_ok(heading, ruta, ruta_split, folders)
    else:
        if not filetools.exists(ruta):
            platformtools.dialog_ok("La cartella non esiste", "Nessun backup salvato")
        else:
            dyesno = platformtools.dialog_yesno("I backup vengono cancellati", "Sei sicuro?")
            if dyesno:
                import shutil
                shutil.rmtree(ruta, ignore_errors=True)


def get_thumbnail_path(thumb_name):
    import urlparse
    web_path = "http://media.tvalacarta.info/pelisalacarta/squares/"
    return urlparse.urljoin(web_path, thumb_name)
