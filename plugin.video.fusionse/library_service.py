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
# Service for updating new episodes on library series
# ------------------------------------------------------------

import imp
import math
import re

from core import config
from core import filetools
from core import jsontools
from core import logger
from core import scrapertools
from core.item import Item
from platformcode import library
from platformcode import platformtools


def create_tvshows_from_xml():
    logger.info("fusionse.platformcode.library_service create_tvshows_from_xml")

    fname = filetools.join(config.get_data_path(), library.TVSHOW_FILE_OLD)
    if filetools.exists(fname):
        platformtools.dialog_ok("Libreria: Si aggiornerà al nuovo formato",
                                 "Selezionare il nome corretto di ogni serie, se non siete sicuri potete 'Annulla'.",
                                 "Ci sono nuove opzioni per la 'Libreria' in 'configurazione'.")

        filetools.rename(library.TVSHOWS_PATH, "SERIES_OLD")

        if not filetools.exists(library.TVSHOWS_PATH):
            filetools.mkdir(library.TVSHOWS_PATH)

            if filetools.exists(library.TVSHOWS_PATH):
                try:
                    data = filetools.read(fname)
                    for line in data.splitlines():
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

                        library.save_library_tvshow(serie, list())

                    filetools.rename(fname, "series.xml.old")

                    # Por ultimo limpia la libreria, por que las rutas anteriores ya no existen
                    library.clean()

                except EnvironmentError:
                    logger.info("ERROR al leer el archivo: {0}".format(fname))

            else:
                logger.info("ERROR, no se ha podido crear la nueva carpeta de SERIES")
        else:
            logger.info("ERROR, no se ha podido renombrar la antigua carpeta de SERIES")

        return True

    return False


def create_tvshows_from_json(_actualizado):
    logger.info("fusionse.platformcode.library_service create_tvshows_from_json")
    fname = filetools.join(config.get_data_path(), library.TVSHOW_FILE)

    if filetools.exists(fname):
        if not _actualizado:
            platformtools.dialog_ok("Libreria: Aggiornamento formato",
                                     "Si prega di attendere la fine del processo")

        try:
            data = jsontools.loads(filetools.read(fname))
            for tvshow in data:
                for channel in data[tvshow]["channels"]:

                    serie = Item(contentSerieName=data[tvshow]["channels"][channel]["tvshow"],
                                 url=data[tvshow]["channels"][channel]["url"], channel=channel, action="episodios",
                                 title=data[tvshow]["name"], active=True)
                    if not tvshow.startswith("t_"):
                        serie.infoLabels["tmdb_id"] = tvshow
                    library.save_library_tvshow(serie, list())

            filetools.rename(fname, "series.json.old")

        except EnvironmentError:
            logger.info("ERROR al leer el archivo: {0}".format(fname))


def main():
    if scrapertools.wait_for_internet(retry=10):

        if config.get_setting("updatechannels") == "true":
            # -- Update channels from repository fusionse ------
            try:
                from core import update_channels
            except:
                logger.info("fusionse.library_service Error in update_channels")
            # ----------------------------------------------------------------------

            # -- Update servertools and servers from repository fusionse ------
            try:
                from core import update_servers
            except:
                logger.info("fusionse.library_service Error in update_servers")
            # ----------------------------------------------------------------------

        logger.info("fusionse.library_service Actualizando series...")
        p_dialog = None

        try:

            if config.get_setting("updatelibrary") == "true":
                heading = 'Aggiornamento biblioteca....'
                p_dialog = platformtools.dialog_progress_bg('fusionse', heading)
                p_dialog.update(0, '')
                show_list = []

                for path, folders, files in filetools.walk(library.TVSHOWS_PATH):
                    show_list.extend([filetools.join(path, f) for f in files if f == "tvshow.json"])

                # fix float porque la division se hace mal en python 2.x
                t = float(100) / len(show_list)

                for i, tvshow_file in enumerate(show_list):
                    serie = Item().fromjson(filetools.read(tvshow_file))
                    path = filetools.dirname(tvshow_file)

                    logger.info("fusionse.library_service serie=" + serie.contentSerieName)
                    logger.info("fusionse.library_service Actualizando " + path)
                    logger.info("fusionse.library_service url " + serie.url)
                    show_name = serie.contentTitle
                    if show_name == "":
                        show_name = serie.show
                    p_dialog.update(int(math.ceil((i + 1) * t)), heading, show_name)

                    # si la serie esta activa se actualiza
                    if serie.active:

                        try:
                            pathchannels = filetools.join(config.get_runtime_path(), "channels", serie.channel + '.py')
                            logger.info("fusionse.library_service Cargando canal: " + pathchannels + " " +
                                        serie.channel)

                            obj = imp.load_source(serie.channel, pathchannels)
                            itemlist = obj.episodios(serie)

                            try:
                                library.save_library_episodes(path, itemlist, serie, True)
                            except Exception as ex:
                                logger.info("fusionse.library_service Error al guardar los capitulos de la serie")
                                template = "An exception of type {0} occured. Arguments:\n{1!r}"
                                message = template.format(type(ex).__name__, ex.args)
                                logger.info(message)

                        except Exception as ex:
                            logger.error("Error al obtener los episodios de: {0}".
                                         format(serie.show))
                            template = "An exception of type {0} occured. Arguments:\n{1!r}"
                            message = template.format(type(ex).__name__, ex.args)
                            logger.info(message)

                p_dialog.close()

            else:
                logger.info("No actualiza la biblioteca, está desactivado en la configuración de fusionse")

        except Exception as ex:
            logger.info("fusionse.library_service Se ha producido un error al actualizar las series")
            template = "An exception of type {0} occured. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            logger.info(message)

            if p_dialog:
                p_dialog.close()


if __name__ == "__main__":
    actualizado = create_tvshows_from_xml()
    create_tvshows_from_json(actualizado)
    main()
