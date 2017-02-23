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
# --------------------------------------------------------------------------------

import re

from core import logger
from core import scrapertools
from core.item import InfoLabels
from core.tmdb import Tmdb
from core import tmdb
from platformcode import platformtools

scraper_global = None


def find_and_set_infoLabels(item):
    """
    función que se llama para buscar y setear los infolabels
    :param item:
    :return:
    """

    global scraper_global
    logger.debug("item:\n" + item.tostring('\n'))

    params = {}

    if item.contentType == "movie":
        tipo_contenido = "film"
        title = item.contentTitle
        # get scraper pelis
        scraper = Tmdb()
        # para tmdb
        tipo_busqueda = "movie"

    else:
        tipo_contenido = "serie"
        title = item.contentSerieName
        # get scraper series
        scraper = Tmdb()
        # para tmdb
        tipo_busqueda = "tv"

    # esto ya está en el scraper tmdb
    # title = re.sub('\[\\\?(B|I|COLOR)\s?[^\]]*\]', '', title)

    # Si el titulo incluye el (año) se lo quitamos
    year = scrapertools.find_single_match(title, "^.+?\s*(\(\d{4}\))$")
    if year:
        title = title.replace(year, "").strip()
        item.infoLabels['year'] = year[1:-1]

    scraper_result = None
    results = []
    while not scraper_result:
        # para tmdb
        if isinstance(scraper, Tmdb):
            logger.debug("scraper es Tmbdb")
            params["texto_buscado"] = title
            params["tipo"] = tipo_busqueda
            params["year"] = item.infoLabels['year']

        if not results:
            if not item.infoLabels.get("tmdb_id"):
                if not item.infoLabels.get("imdb_id"):
                    scraper_global = scraper(**params)
                else:
                    logger.info("tiene imdb")
                    # para tmdb
                    if isinstance(scraper, Tmdb):
                        params["external_id"] = item.infoLabels.get("imdb_id")
                        params["external_source"] = "imdb_id"

                    scraper_global = scraper(**params)

            elif not scraper_global or scraper_global.result.get("id") != item.infoLabels['tmdb_id']:
                # para tmdb
                if isinstance(scraper, Tmdb):
                    params["id_Tmdb"] = item.infoLabels['tmdb_id']
                    params["idioma_busqueda"] = "it"

                scraper_global = scraper(**params)

            results = scraper_global.get_list_resultados()

        if len(results) > 1:
            scraper_result = platformtools.show_video_info(results, item=item, scraper=scraper,
                                                           caption="[%s]: Selezionare la %s corretta"
                                                                   % (title, tipo_contenido))

        elif len(results) > 0:
            scraper_result = results[0]

        if scraper_result is None:
            index = -1
            if tipo_contenido == "serie":
                # Si no lo encuentra la serie por si solo, presentamos una lista de opciones
                opciones = ["Immettere un altro nome", "Ricerca TheTvDB.com"]
                index = platformtools.dialog_select("%s non trovato" % tipo_contenido.capitalize(), opciones)

            elif platformtools.dialog_yesno("Film non trovato", "Non ho trovato il film:", title,
                                            'Vuoi inserire un altro nome?'):
                index = 0

            if index < 0:
                logger.debug("he pulsado 'cancelar' en la ventana '%s no encontrada'" % tipo_contenido.capitalize())
                break

            if index == 0: # "Introducir otro nombre"
                # Pregunta el titulo
                it = platformtools.dialog_input(title, "Inserire il nome del %s per la ricerca" % tipo_contenido)
                if it is not None:
                    title = it
                    item.infoLabels['year'] = ""
                    # reseteamos los resultados
                    results = []
                else:
                    logger.debug("he pulsado 'cancelar' en la ventana 'introduzca el nombre correcto'")
                    break

            if index == 1: # "Buscar en TheTvDB.com"
                results = tvdb_series_by_title(title)

    if isinstance(item.infoLabels, InfoLabels):
        infoLabels = item.infoLabels
    else:
        infoLabels = InfoLabels()

    if scraper_result:
        if 'id' in scraper_result:
            # resultados obtenidos de tmdb
            infoLabels['tmdb_id'] = scraper_result['id']
            infoLabels['url_scraper'] = "https://www.themoviedb.org/tv/%s" % infoLabels['tmdb_id']
            item.infoLabels = infoLabels
            tmdb.set_infoLabels_item(item)

        elif 'tvdb_id' in scraper_result:
            # resultados obtenidos de tvdb
            infoLabels.update(scraper_result)
            item.infoLabels = infoLabels

        # logger.debug("item:\n" + item.tostring('\n'))
        return True
    else:
        item.infoLabels = infoLabels
        return False


class Scraper(object):
    def __init__(self):
        pass

    def search(self):
        pass


def tvdb_series_by_title(title, idioma="it"):
    list_series = []
    limite = 8

    SeriesByTitleUrl = 'http://thetvdb.com/api/GetSeries.php?seriesname=%s&language=%s' % \
                       (title.replace(' ', '%20'), idioma)
    data = scrapertools.cache_page(SeriesByTitleUrl)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = '<Series>(.*?)</Series>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for serie in matches:
        info = {"type": "tv", "mediatype": "tvshow"}
        info["imdb_id"] = scrapertools.find_single_match(serie, '<IMDB_ID>([^<]*)</IMDB_ID>')
        if info["imdb_id"]:
            info["title"] = scrapertools.find_single_match(serie, '<SeriesName>([^<]*)</SeriesName>')
            #info["date"] = scrapertools.find_single_match(serie, '<FirstAired>([^<]*)</FirstAired>')
            info["tvdb_id"] = scrapertools.find_single_match(serie, '<id>([^<]*)</id>')
            info["plot"] = scrapertools.find_single_match(serie, '<Overview>([^<]*)</Overview>')
            info["url_scraper"] = "http://thetvdb.com/?tab=series&id=" + info["tvdb_id"]

            # Recuperar imagenes
            BannersBySeriesIdUrl = 'http://thetvdb.com/api/1D62F2F90030C444/series/%s/banners.xml' % info["tvdb_id"]
            data = scrapertools.cache_page(BannersBySeriesIdUrl)
            data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

            patron = '<Banner>(.*?)</Banner>'
            banners = scrapertools.find_multiple_matches(data, patron)
            for banner in banners:
                BannerType =  scrapertools.find_single_match(banner, '<BannerType>([^<]*)</BannerType>')
                if BannerType == 'fanart' and not "fanart" in info:
                    info["fanart"] = 'http://thetvdb.com/banners/' + \
                                     scrapertools.find_single_match(banner, '<BannerPath>([^<]*)</BannerPath>')
                if BannerType == 'poster' and not "thumbnail" in info:
                    info["thumbnail"] = 'http://thetvdb.com/banners/' + \
                                     scrapertools.find_single_match(banner, '<BannerPath>([^<]*)</BannerPath>')
                if "fanart" in info and "thumbnail" in info:
                    break


            list_series.append(info)
            limite -= 1
            if limite == 0:
                break

    #logger.debug(list_series)
    return list_series
