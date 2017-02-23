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
# Service for updating new episodes on library series
# ------------------------------------------------------------

import imp
import math
import re
import datetime

from core import config
from core import filetools
from core import jsontools
from core import logger
from core import scrapertools
from core.item import Item
from core import library
from platformcode import xbmc_library
from platformcode import platformtools


def convert_old_to_v4():
    logger.info()
    path_series_xml = filetools.join(config.get_data_path(), "series.xml")
    path_series_json = filetools.join(config.get_data_path(), "series.json")
    series_insertadas = 0
    series_fallidas = 0
    version = 'v?'

    # Renombrar carpeta Series y crear una vacia
    import time
    new_name = str(time.time())
    path_series_old = filetools.join(library.LIBRARY_PATH, "SERIES_OLD_" + new_name)
    if filetools.rename(library.TVSHOWS_PATH,  "SERIES_OLD_" + new_name):
        if not filetools.mkdir(library.TVSHOWS_PATH):
            logger.error("ERROR, no se ha podido crear la nueva carpeta de SERIES")
            return False
    else:
        logger.error("ERROR, no se ha podido renombrar la antigua carpeta de SERIES")
        return False

    path_cine_old = filetools.join(library.LIBRARY_PATH, "CINE_OLD_" + new_name)
    if filetools.rename(library.MOVIES_PATH,  "CINE_OLD_" + new_name):
        if not filetools.mkdir(library.MOVIES_PATH):
            logger.error("ERROR, no se ha podido crear la nueva carpeta de CINE")
            return False
    else:
        logger.error("ERROR, no se ha podido renombrar la antigua carpeta de CINE")
        return False

    # Convertir libreria de v1(xml) a v4
    if filetools.exists(path_series_xml):
        try:
            data = filetools.read(path_series_xml)
            for line in data.splitlines():
                try:
                    aux = line.rstrip('\n').split(",")
                    tvshow = aux[0].strip()
                    url = aux[1].strip()
                    channel = aux[2].strip()

                    serie = Item(contentSerieName=tvshow, url=url, channel=channel, action="episodios",
                                 title=tvshow, active=True)

                    patron = "^(.+)[\s]\((\d{4})\)$"
                    matches = re.compile(patron, re.DOTALL).findall(serie.contentSerieName)

                    if matches:
                        serie.infoLabels['title'] = matches[0][0]
                        serie.infoLabels['year'] = matches[0][1]
                    else:
                        serie.infoLabels['title'] = tvshow

                    insertados, sobreescritos, fallidos = library.save_library_tvshow(serie, list())
                    if fallidos == 0:
                        series_insertadas += 1
                        platformtools.dialog_notification("Serie aggiornata", serie.infoLabels['title'])
                    else:
                        series_fallidas += 1
                except:
                    series_fallidas += 1

            filetools.rename(path_series_xml, "series.xml.old")
            version = 'v4'

        except EnvironmentError:
            logger.error("ERROR al leer el archivo: %s" % path_series_xml)
            return False

    # Convertir libreria de v2(json) a v4
    if filetools.exists(path_series_json):
        try:
            data = jsontools.load_json(filetools.read(path_series_json))
            for tvshow in data:
                for channel in data[tvshow]["channels"]:
                    try:
                        serie = Item(contentSerieName=data[tvshow]["channels"][channel]["tvshow"],
                                     url=data[tvshow]["channels"][channel]["url"], channel=channel, action="episodios",
                                     title=data[tvshow]["name"], active=True)
                        if not tvshow.startswith("t_"):
                            serie.infoLabels["tmdb_id"] = tvshow

                        insertados, sobreescritos, fallidos = library.save_library_tvshow(serie, list())
                        if fallidos == 0:
                            series_insertadas += 1
                            platformtools.dialog_notification("Serie aggiornata", serie.infoLabels['title'])
                        else:
                            series_fallidas += 1
                    except:
                        series_fallidas += 1

            filetools.rename(path_series_json, "series.json.old")
            version = 'v4'

        except EnvironmentError:
            logger.error("ERROR al leer el archivo: %s" % path_series_json)
            return False

    # Convertir libreria de v3 a v4
    if version != 'v4':
        # Obtenemos todos los tvshow.json de la biblioteca de SERIES_OLD recursivamente
        for raiz, subcarpetas, ficheros in filetools.walk(path_series_old):
            for f in ficheros:
                if f == "tvshow.json":
                    try:
                        serie = Item().fromjson(filetools.read(filetools.join(raiz, f)))
                        insertados, sobreescritos, fallidos = library.save_library_tvshow(serie, list())
                        if fallidos == 0:
                            series_insertadas += 1
                            platformtools.dialog_notification("Serie actualizada", serie.infoLabels['title'])
                        else:
                            series_fallidas += 1
                    except:
                        series_fallidas += 1

        movies_insertadas = 0
        movies_fallidas = 0
        for raiz, subcarpetas, ficheros in filetools.walk(path_cine_old):
            for f in ficheros:
                if f.endswith(".strm.json"):
                    try:
                        movie= Item().fromjson(filetools.read(filetools.join(raiz, f)))
                        insertados, sobreescritos, fallidos = library.save_library_movie(movie)
                        if fallidos == 0:
                            movies_insertadas += 1
                            platformtools.dialog_notification("Película actualizada", movie.infoLabels['title'])
                        else:
                            movies_fallidas += 1
                    except:
                        movies_fallidas += 1


    config.set_setting("library_version", 'v4')

    platformtools.dialog_notification("Libreria aggiornata con il nuovo formato",
                                      "%s serie convertite e %s serie scaricate. Continuare per"
                                      "ottenere le info sugli episodi" %
                                      (series_insertadas, series_fallidas), time=12000)

    # Por ultimo limpia la libreria, por que las rutas anteriores ya no existen
    xbmc_library.clean()

    return True


def update(path, p_dialog, i, t, serie, overwrite):
    logger.info("Actualizando " + path)
    insertados_total = 0

    # logger.debug("%s: %s" %(serie.contentSerieName,str(list_canales) ))
    for channel, url in serie.library_urls.items():
        serie.channel = channel
        serie.url = url

        heading = 'Aggiornando la libreria....'
        p_dialog.update(int(math.ceil((i + 1) * t)), heading, "%s: %s" % (serie.contentSerieName,
                                                                          serie.channel.capitalize()))
        try:
            pathchannels = filetools.join(config.get_runtime_path(), "channels", serie.channel + '.py')
            logger.info("Cargando canal: " + pathchannels + " " +
                        serie.channel)

            if serie.library_filter_show:
                serie.show = serie.library_filter_show.get(channel, serie.contentSerieName)

            obj = imp.load_source(serie.channel, pathchannels)
            itemlist = obj.episodios(serie)

            try:
                insertados, sobreescritos, fallidos = library.save_library_episodes(path, itemlist, serie, silent=True,
                                                                                    overwrite=overwrite)
                insertados_total += insertados

            except Exception as ex:
                logger.info("Error al guardar los capitulos de la serie")
                template = "An exception of type {0} occured. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                logger.info(message)

        except Exception as ex:
            logger.error("Error al obtener los episodios de: {0}".
                         format(serie.show))
            template = "An exception of type {0} occured. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            logger.info(message)

    return insertados_total > 0


def check_for_update(overwrite=True):
    logger.info("Actualizando series...")
    logger.info("Overwrite? -> " + str(overwrite))
    p_dialog = None
    serie_actualizada = False
    hoy = datetime.date.today()

    overwrite_everything = False
    try:
        if overwrite == "everything":
            overwrite = True
            overwrite_everything = True
        if config.get_setting("updatelibrary", "biblioteca") != 0 or overwrite:
            config.set_setting("updatelibrary_last_check", hoy.strftime('%Y-%m-%d'), "biblioteca")

            if config.get_setting("updatelibrary", "biblioteca") == 1 and not overwrite:
                # "Actualizar al inicio" y No venimos del canal configuracion
                updatelibrary_wait = [0, 10000, 20000, 30000, 60000]
                wait = updatelibrary_wait[int(config.get_setting("updatelibrary_wait", "biblioteca"))]
                if wait > 0:
                    import xbmc
                    xbmc.sleep(wait)

            heading = 'Aggiornando la libreria....'
            p_dialog = platformtools.dialog_progress_bg('streamondemand', heading)
            p_dialog.update(0, '')
            show_list = []

            for path, folders, files in filetools.walk(library.TVSHOWS_PATH):
                show_list.extend([filetools.join(path, f) for f in files if f == "tvshow.nfo"])

            if show_list:
                t = float(100) / len(show_list)

            for i, tvshow_file in enumerate(show_list):
                head_nfo, serie = library.read_nfo(tvshow_file)
                path = filetools.dirname(tvshow_file)

                logger.info("serie=" + serie.contentSerieName)
                p_dialog.update(int(math.ceil((i+1) * t)), heading, serie.contentSerieName)

                interval = int(serie.active)  # Podria ser del tipo bool

                if not serie.active:
                    # si la serie no esta activa descartar
                    continue

                # obtenemos las fecha de auctualizacion y de la proxima programada para esta serie
                update_next = serie.update_next
                if update_next:
                    y, m, d = update_next.split('-')
                    update_next = datetime.date(int(y), int(m), int(d))
                else:
                    update_next = hoy

                update_last = serie.update_last
                if update_last:
                    y, m, d = update_last.split('-')
                    update_last = datetime.date(int(y), int(m), int(d))
                else:
                    update_last = hoy

                # si la serie esta activa ...
                if overwrite or config.get_setting("updatetvshows_interval", "biblioteca") == 0:
                    # ... forzar actualizacion independientemente del intervalo
                    if overwrite_everything:
                        overwrite = "everything"
                    serie_actualizada = update(path, p_dialog, i, t, serie, overwrite)

                elif interval == 1 and update_next <= hoy:
                    # ...actualizacion diaria
                    serie_actualizada = update(path, p_dialog, i, t, serie, overwrite)
                    if not serie_actualizada and update_last <= hoy - datetime.timedelta(days=7):
                        # si hace una semana q no se actualiza, pasar el intervalo a semanal
                        interval = 7
                        update_next = hoy + datetime.timedelta(days=interval)

                elif interval == 7 and update_next <= hoy:
                    # ...actualizacion semanal
                    serie_actualizada = update(path, p_dialog, i, t, serie, overwrite)
                    if not serie_actualizada:
                        if update_last <= hoy - datetime.timedelta(days=14):
                            # si hace 2 semanas q no se actualiza, pasar el intervalo a mensual
                            interval = 30

                        update_next += datetime.timedelta(days=interval)

                elif interval == 30 and update_next <= hoy:
                    # ...actualizacion mensual
                    serie_actualizada = update(path, p_dialog, i, t, serie, overwrite)
                    if not serie_actualizada:
                        update_next += datetime.timedelta(days=interval)

                if interval != int(serie.active) or update_next.strftime('%Y-%m-%d') != serie.update_next:
                    serie.active = interval
                    serie.update_next = update_next.strftime('%Y-%m-%d')
                    serie.channel = "biblioteca"
                    serie.action = "get_temporadas"
                    filetools.write(tvshow_file, head_nfo + serie.tojson())

                if serie_actualizada:
                    # Actualizamos la biblioteca de Kodi
                    xbmc_library.update(folder=filetools.basename(path))

            p_dialog.close()

        else:
            logger.info("No actualiza la biblioteca, está desactivado en la configuración de streamondemand")

    except Exception as ex:
        logger.error("Se ha producido un error al actualizar las series")
        template = "An exception of type {0} occured. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        logger.error(message)

        if p_dialog:
            p_dialog.close()


if __name__ == "__main__":
    if scrapertools.wait_for_internet(retry=10):
        if config.get_setting("check_for_channel_updates") == "true":
            # -- Update channels from repository streamondemand ------
            try:
                from core import update_channels
            except:
                logger.info("streamondemand.library_service Error in update_channels")
            # ----------------------------------------------------------------------

            # -- Update servertools and servers from repository streamondemand ------
            try:
                from core import update_servers
            except:
                logger.info("streamondemand.library_service Error in update_servers")
            # ----------------------------------------------------------------------

        # Se ejecuta en cada inicio
        if config.get_setting("library_version") != 'v4':
            platformtools.dialog_ok(config.PLUGIN_NAME.capitalize(), "Aggiornamento della libreria al nuovo formato",
                                    "Selezionare correttamente il nome della serie, se non sicuro seleziona 'Annulla'.")

            if not convert_old_to_v4():
                platformtools.dialog_ok(config.PLUGIN_NAME.capitalize(),
                                        "ERROR, nella conversione al nuovo formato")
            else:
                check_for_update(overwrite=False)
        else:
            check_for_update(overwrite=False)

    # Se ejecuta ciclicamente
    import xbmc
    version_xbmc = int(xbmc.getInfoLabel("System.BuildVersion").split(".", 1)[0])

    if version_xbmc >= 14:
        monitor = xbmc.Monitor()  # For Kodi >= 14
    else:
        monitor = None  # For Kodi < 14

    if monitor:
        while not monitor.abortRequested():
            if config.get_setting("updatelibrary", "biblioteca") == 2:  # "Actualizar...Cada dia
                hoy = datetime.date.today()
                last_check = config.get_setting("updatelibrary_last_check", "biblioteca")
                if last_check:
                    y, m, d = last_check.split('-')
                    last_check = datetime.date(int(y), int(m), int(d))
                else:
                    last_check = hoy - datetime.timedelta(days=1)

                if last_check < hoy and datetime.datetime.now().hour >= 4:
                    logger.info("Inicio actualización programada: %s" % datetime.datetime.now())
                    check_for_update(overwrite=False)

            if monitor.waitForAbort(3600):  # cada hora
                break

    else:
        while not xbmc.abortRequested:
            if config.get_setting("updatelibrary", "biblioteca") == 2:  # "Actualizar...Cada dia
                hoy = datetime.date.today()
                last_check = config.get_setting("updatelibrary_last_check", "biblioteca")
                if last_check:
                    y, m, d = last_check.split('-')
                    last_check = datetime.date(int(y), int(m), int(d))
                else:
                    last_check = hoy - datetime.timedelta(days=1)

                if last_check < hoy and datetime.datetime.now().hour >= 4:
                    logger.info("Inicio actualización programada: %s" % datetime.datetime.now())
                    check_for_update(overwrite=False)

            xbmc.sleep(3600)
