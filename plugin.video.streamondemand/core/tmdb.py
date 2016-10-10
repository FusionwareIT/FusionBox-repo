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

import copy
import re
import time

from core import jsontools
from core import logger
from core import scrapertools
from platformcode import platformtools

# -----------------------------------------------------------------------------------------------------------
# Conjunto de funciones relacionadas con las infoLabels.
#   version 1.0:
#       Version inicial
#
#   Incluyen:
#       set_infoLabels(source, seekTmdb, idioma_busqueda): Obtiene y fija (item.infoLabels) los datos extras de una o
# varias series, capitulos o peliculas.
#       set_infoLabels_item(item, seekTmdb, idioma_busqueda): Obtiene y fija (item.infoLabels) los datos extras de una
# serie, capitulo o pelicula.
#       set_infoLabels_itemlist(item_list, seekTmdb, idioma_busqueda): Obtiene y fija (item.infoLabels) los datos
# extras de una lista de series, capitulos o peliculas.
#       infoLabels_tostring(item): Retorna un str con la lista ordenada con los infoLabels del item
#
#   Uso:
#       tmdb.set_infoLabels(item, seekTmdb = True)
#
#       Obtener datos basicos de una pelicula:
#           Antes de llamar al metodo set_infoLabels el titulo a buscar debe estar en item.fulltitle
#           o en item.contentTitle y el año en item.infoLabels['year'].
#
#       Obtener datos basicos de una serie:
#           Antes de llamar al metodo set_infoLabels el titulo a buscar debe estar en item.show o en
# item.contentSerieName.
#
#       Obtener mas datos de una pelicula o serie:
#           Despues de obtener los datos basicos en item.infoLabels['tmdb'] tendremos el codigo de la serie o pelicula.
#           Tambien podriamos directamente fijar este codigo, si se conoce, o utilizar los codigo correspondientes de:
#           IMDB (en item.infoLabels['IMDBNumber'] o item.infoLabels['code'] o item.infoLabels['imdb_id']), TVDB
# (solo series, en item.infoLabels['tvdb_id']),
#           Freebase (solo series, en item.infoLabels['freebase_mid']),TVRage (solo series, en
# item.infoLabels['tvrage_id'])
#
#       Obtener datos de una temporada:
#           Antes de llamar al metodo set_infoLabels el titulo de la serie debe estar en item.show o en
# item.contentSerieName,
#           el codigo TMDB de la serie debe estar en item.infoLabels['tmdb'] (puede fijarse automaticamente mediante
# la consulta de datos basica)
#           y el numero de temporada debe estar en item.infoLabels['season'].
#
#       Obtener datos de un episodio:
#           Antes de llamar al metodo set_infoLabels el titulo de la serie debe estar en item.show o en
# item.contentSerieName,
#           el codigo TMDB de la serie debe estar en item.infoLabels['tmdb'] (puede fijarse automaticamente mediante la
# consulta de datos basica),
#           el numero de temporada debe estar en item.infoLabels['season'] y el numero de episodio debe estar en
# item.infoLabels['episode'].
#
#
# --------------------------------------------------------------------------------------------------------------

otmdb_global = None


def cb_select_from_tmdb(item, tmdb_result):
    if tmdb_result is None:
        logger.debug("he pulsado 'cancelar' en la ventana de info de la serie/pelicula")
        return None
    else:
        return tmdb_result


def find_and_set_infoLabels_tmdb(item, ask_video=True):
    global otmdb_global

    contentType = item.contentType if item.contentType else ("movie" if not item.contentSerieName else "tvshow")
    title = item.contentSerieName if contentType == "tvshow" else item.contentTitle
    season = int(item.contentSeason) if item.contentSeason else ""
    episode = int(item.contentEpisodeNumber) if item.contentEpisodeNumber else ""
    contentType = "episode" if contentType == "tvshow" and item.contentSeason and item.contentEpisodeNumber else \
        contentType
    year = item.infoLabels.get('year', '')

    video_type = "tv" if contentType in ["tvshow", "episode"] else "movie"

    tmdb_result = None
    while not tmdb_result:
        if not item.infoLabels.get("tmdb_id"):
            otmdb_global = Tmdb(texto_buscado=title, tipo=video_type, year=year)
        elif not otmdb_global or otmdb_global.result.get("id") != item.infoLabels['tmdb_id']:
            otmdb_global = Tmdb(id_Tmdb=item.infoLabels['tmdb_id'], tipo=video_type, idioma_busqueda="es")

        results = otmdb_global.get_list_resultados()


        if len(results) > 1 and ask_video:
            tmdb_result = platformtools.show_video_info(results, caption="[{0}]: Selecciona la {1} correcta"
                                                        .format(title, "serie" if video_type == "tv" else "pelicula"),
                                                        callback='cb_select_from_tmdb', item=item)
        elif len(results) > 0:
            tmdb_result = results[0]


        if tmdb_result is None:
            if platformtools.dialog_yesno("{0} no encontrada".
                                          format("Serie" if video_type == "tv" else "Pelicula") ,
                                          "No se ha encontrado la {0}:".
                                          format("serie" if video_type == "tv" else "pelicula"),
                                          title,
                                          '¿Desea introducir otro nombre?'):
                # Pregunta el titulo
                it = platformtools.dialog_input(title, "Introduzca el nombre de la {0} a buscar".
                                                format("serie" if video_type == "tv" else "pelicula"))
                if it is not None:
                    title = it
                else:
                    logger.debug("he pulsado 'cancelar' en la ventana 'introduzca el nombre correcto'")
                    break
            else:
                break


    infoLabels = item.infoLabels if type(item.infoLabels) == dict else {}

    if not tmdb_result:
        item.infoLabels = infoLabels
        return False

    infoLabels = otmdb_global.get_infoLabels(infoLabels, tmdb_result)
    infoLabels["mediatype"] = contentType

    if infoLabels["mediatype"] == "episode":
        try:
            episodio = otmdb_global.get_episodio(season, episode)
        except:
            pass
            # No se ha podido buscar
        else:
            if episodio:
                # Actualizar datos
                infoLabels['title'] = episodio['episodio_titulo']
                infoLabels['season'] = season
                infoLabels['episode'] = episode
                if episodio['episodio_sinopsis']:
                    infoLabels['plot'] = episodio['episodio_sinopsis']
                if episodio['episodio_imagen']:
                    infoLabels['thumbnail'] = episodio['episodio_imagen']

    item.infoLabels = infoLabels
    return True


def set_infoLabels_item(item, seekTmdb=True, idioma_busqueda='it', lock=None):
    # -----------------------------------------------------------------------------------------------------------
    # Obtiene y fija (item.infoLabels) los datos extras de una serie, capitulo o pelicula.
    #
    #   Parametros:
    #       item: (Item) Objeto Item que representa un pelicula, serie o capitulo. El diccionario item.infoLabels sera
    #               modificado incluyendo los datos extras localizados.
    #       (opcional) seekTmdb: (bool) Si es True hace una busqueda en www.themoviedb.org para obtener los datos,
    #                   en caso contrario obtiene los datos del propio Item si existen.
    #       (opcional) idioma_busqueda: (str) Codigo del idioma segun ISO 639-1, en caso de busqueda en
    # www.themoviedb.org.
    #   Retorna:
    #       Un numero cuyo valor absoluto representa la cantidad de elementos incluidos en el diccionario
    # item.infoLabels.
    #       Este numero sera positivo si los datos se han obtenido de www.themoviedb.org y negativo en caso contrario.
    # ---------------------------------------------------------------------------------------------------------

    global otmdb_global

    def __inicializar():
        # Inicializar con valores por defecto
        if 'year' not in item.infoLabels:
            item.infoLabels['year'] = ''
        if 'IMDBNumber' not in item.infoLabels:
            item.infoLabels['IMDBNumber'] = ''
        if 'code' not in item.infoLabels:
            item.infoLabels['code'] = ''
        if 'imdb_id' not in item.infoLabels:
            item.infoLabels['imdb_id'] = ''
        if 'plot' not in item.infoLabels:
            item.infoLabels['plot'] = item.plot if item.plot != '' else item.contentPlot
        if 'genre' not in item.infoLabels:
            item.infoLabels['genre'] = item.category
        item.infoLabels['duration'] = item.duration
        item.infoLabels['AudioLanguage'] = item.language
        titulo = item.fulltitle if item.fulltitle != '' else \
            (item.contentTitle if item.contentTitle != '' else item.title)
        if 'title' not in item.infoLabels:
            item.infoLabels['title'] = titulo
        item.infoLabels['tvshowtitle'] = item.show if item.show != '' else item.contentSerieName
        if 'mediatype' not in item.infoLabels:
            item.infoLabels['mediatype'] = 'movie' if item.infoLabels['tvshowtitle'] == '' else 'tvshow'

    def obtener_datos_item():
        if item.contentSeason != '':
            item.infoLabels['mediatype'] = 'season'
        if item.contentEpisodeNumber != '' or item.contentEpisodeTitle != '':
            item.infoLabels['mediatype'] = 'episode'
        if item.contentTitle == '':
            item.contentTitle = item.title
        return -1 * len(item.infoLabels)

    def __leer_datos(otmdb_aux):
        item.infoLabels = otmdb_aux.get_infoLabels(item.infoLabels)
        if 'thumbnail' in item.infoLabels:
            item.thumbnail = item.infoLabels['thumbnail']
        if 'fanart' in item.infoLabels:
            item.fanart = item.infoLabels['fanart']

    if seekTmdb:
        # Comprobamos q tipo de contenido es...
        if 'mediatype' not in item.infoLabels:
            item.infoLabels['tvshowtitle'] = item.show if item.show != '' else item.contentSerieName
            item.infoLabels['mediatype'] = 'movie' if item.infoLabels['tvshowtitle'] == '' else 'tvshow'
        tipo = 'movie' if item.infoLabels['mediatype'] == 'movie' else 'tv'
        if 'season' in item.infoLabels and 'tmdb_id' in item.infoLabels:
            try:
                numtemporada = int(item.infoLabels['season'])
            except ValueError:
                logger.debug("El numero de temporada no es valido")
                return obtener_datos_item()


            if lock:
                lock.acquire()
            if not otmdb_global:
                otmdb_global = Tmdb(id_Tmdb=item.infoLabels['tmdb_id'], tipo=tipo, idioma_busqueda=idioma_busqueda)
                __leer_datos(otmdb_global)
                temporada = otmdb_global.get_temporada(numtemporada)
            if lock:
                lock.release()

            if 'episode' in item.infoLabels:
                try:
                    episode = int(item.infoLabels['episode'])
                except ValueError:
                    logger.debug("El número de episodio (%s) no es valido" % repr(item.infoLabels['episode']))
                    return obtener_datos_item()

                # Tenemos numero de temporada y numero de episodio validos...
                # ... buscar datos episodio
                item.infoLabels['mediatype'] = 'episode'
                episodio = otmdb_global.get_episodio(numtemporada, episode)
                if episodio:
                    # Actualizar datos
                    __leer_datos(otmdb_global)
                    item.infoLabels['title'] = episodio['episodio_titulo']
                    if episodio['episodio_sinopsis']:
                        item.infoLabels['plot'] = episodio['episodio_sinopsis']
                    if episodio['episodio_imagen']:
                        item.infoLabels['poster_path'] = episodio['episodio_imagen']
                        item.thumbnail = item.infoLabels['poster_path']
                    if episodio['episodio_air_date']:
                        item.infoLabels['aired'] = episodio['episodio_air_date']
                    if episodio['episodio_vote_average']:
                        item.infoLabels['rating'] = episodio['episodio_vote_average']
                        item.infoLabels['votes'] = episodio['episodio_vote_count']

                    return len(item.infoLabels)

            else:
                # Tenemos numero de temporada valido pero no numero de episodio...
                # ... buscar datos temporada
                item.infoLabels['mediatype'] = 'season'
                temporada = otmdb_global.get_temporada(numtemporada)
                if temporada:
                    # Actualizar datos
                    __leer_datos(otmdb_global)
                    logger.debug(str(item.infoLabels))
                    logger.debug(str(temporada))
                    item.infoLabels['title'] = temporada['name']
                    if temporada['overview']:
                        item.infoLabels['plot'] = temporada['overview']
                    if temporada['air_date']:
                        item.infoLabels['aired'] = temporada['air_date']
                    if temporada['poster_path']:
                        item.infoLabels['poster_path'] = 'http://image.tmdb.org/t/p/original' + temporada['poster_path']
                        item.thumbnail = item.infoLabels['poster_path']

            return len(item.infoLabels)

        # Buscar...
        else:
            __inicializar()
            otmdb = copy.copy(otmdb_global)
            # Busquedas por ID...
            if 'tmdb_id' in item.infoLabels and item.infoLabels['tmdb_id']:
                # ...Busqueda por tmdb_id
                otmdb = Tmdb(id_Tmdb=item.infoLabels['tmdb_id'], tipo=tipo, idioma_busqueda=idioma_busqueda)

            elif item.infoLabels['IMDBNumber'] or item.infoLabels['code'] or item.infoLabels['imdb_id']:
                if item.infoLabels['IMDBNumber']:
                    item.infoLabels['code'] = item.infoLabels['IMDBNumber']
                    item.infoLabels['imdb_id'] = item.infoLabels['IMDBNumber']
                elif item.infoLabels['code']:
                    item.infoLabels['IMDBNumber'] = item.infoLabels['code']
                    item.infoLabels['imdb_id'] = item.infoLabels['code']
                else:
                    item.infoLabels['code'] = item.infoLabels['imdb_id']
                    item.infoLabels['IMDBNumber'] = item.infoLabels['imdb_id']
                # ...Busqueda por imdb code
                otmdb = Tmdb(external_id=item.infoLabels['imdb_id'], external_source="imdb_id", tipo=tipo,
                                    idioma_busqueda=idioma_busqueda)

            elif tipo == 'tv':  # buscar con otros codigos
                if 'tvdb_id' in item.infoLabels and item.infoLabels['tvdb_id']:
                    # ...Busqueda por tvdb_id
                    otmdb = Tmdb(external_id=item.infoLabels['tvdb_id'], external_source="tvdb_id", tipo=tipo,
                                        idioma_busqueda=idioma_busqueda)
                elif 'freebase_mid' in item.infoLabels and item.infoLabels['freebase_mid']:
                    # ...Busqueda por freebase_mid
                    otmdb = Tmdb(external_id=item.infoLabels['freebase_mid'], external_source="freebase_mid",
                                        tipo=tipo, idioma_busqueda=idioma_busqueda)
                elif 'freebase_id' in item.infoLabels and item.infoLabels['freebase_id']:
                    # ...Busqueda por freebase_id
                    otmdb = Tmdb(external_id=item.infoLabels['freebase_id'], external_source="freebase_id",
                                        tipo=tipo, idioma_busqueda=idioma_busqueda)
                elif 'tvrage_id' in item.infoLabels and item.infoLabels['tvrage_id']:
                    # ...Busqueda por tvrage_id
                    otmdb = Tmdb(external_id=item.infoLabels['tvrage_id'], external_source="tvrage_id",
                                        tipo=tipo, idioma_busqueda=idioma_busqueda)

            if otmdb is None:
                # No se ha podido buscar por ID...
                # hacerlo por titulo
                if item.infoLabels['title'] != '':
                    if tipo == 'tv':
                        # Busqueda de serie por titulo y filtrando sus resultados si es necesario
                        otmdb = Tmdb(texto_buscado=item.infoLabels['tvshowtitle'], tipo=tipo,
                                            idioma_busqueda=idioma_busqueda, filtro=item.infoLabels.get('filtro', {}),
                                            year=str(item.infoLabels.get('year', '')))
                    else:
                        # Busqueda de pelicula por titulo...
                        if item.infoLabels['year'] or 'filtro' in item.infoLabels:
                            # ...y año o filtro
                            titulo_buscado = item.fulltitle if item.fulltitle != '' else item.contentTitle
                            otmdb = Tmdb(texto_buscado=titulo_buscado, tipo=tipo,
                                         idioma_busqueda=idioma_busqueda,
                                         filtro=item.infoLabels.get('filtro', {}),
                                         year=str(item.infoLabels.get('year', '')))

            if otmdb is None or not otmdb.get_id():
                # La busqueda no ha dado resultado
                return obtener_datos_item()
            else:
                # La busqueda ha encontrado un resultado valido
                __leer_datos(otmdb)
                return len(item.infoLabels)

    else:
        __inicializar()
        return obtener_datos_item()


def set_infoLabels_itemlist(item_list, seekTmdb=False, idioma_busqueda='it'):
    """
    De manera concurrente, obtiene los datos de los items incluidos en la lista item_list.

    La API tiene un limite de 40 peticiones por IP cada 10'' y por eso la lista no deberia tener mas de 30 items
    para asegurar un buen funcionamiento de esta funcion.

    :param item_list: listado de objetos Item que representan peliculas, series o capitulos. El diccionario
        item.infoLabels de cada objeto Item sera modificado incluyendo los datos extras localizados.
    :type item_list: list
    :param seekTmdb: Si es True hace una busqueda en www.themoviedb.org para obtener los datos, en caso contrario
        obtiene los datos del propio Item si existen.
    :type seekTmdb: bool
    :param idioma_busqueda: Codigo del idioma segun ISO 639-1, en caso de busqueda en www.themoviedb.org.
    :type idioma_busqueda: str

    :return: Una lista de numeros cuyo valor absoluto representa la cantidad de elementos incluidos en el diccionario
        item.infoLabels de cada Item. Este numero sera positivo si los datos se han obtenido de www.themoviedb.org y
        negativo en caso contrario.
    :rtype: list
    """
    import threading

    semaforo = threading.Semaphore(20)
    lock = threading.Lock()
    r_list = list()
    i = 0
    l_hilo = list()

    def sub_get(item, _i, _seekTmdb):
        semaforo.acquire()
        ret = set_infoLabels_item(item, _seekTmdb, idioma_busqueda, lock)
        # logger.debug(str(ret) + "item: " + item.tostring())
        semaforo.release()
        r_list.append((_i, item, ret))

    for item in item_list:
        t = threading.Thread(target=sub_get, args=(item, i, seekTmdb))
        t.start()
        i += 1
        l_hilo.append(t)

    # esperar q todos los hilos terminen
    for x in l_hilo:
        x.join()

    # Ordenar lista de resultados por orden de llamada para mantener el mismo orden q item_list
    r_list.sort(key=lambda i: i[0])

    # Reconstruir y devolver la lista solo con los resultados de las llamadas individuales
    return [ii[2] for ii in r_list]


def set_infoLabels(source, seekTmdb=False, idioma_busqueda='it'):
    """
    Dependiendo del tipo de dato de source obtiene y fija (item.infoLabels) los datos extras de una o varias series,
    capitulos o peliculas.

    @param source: variable que contiene la información para establecer infoLabels
    @type source: list, item
    @param seekTmdb: si es True hace una busqueda en www.themoviedb.org para obtener los datos, en caso contrario
        obtiene los datos del propio Item.
    @type seekTmdb: bool
    @param idioma_busqueda: fija el valor de idioma en caso de busqueda en www.themoviedb.org
    @type idioma_busqueda: str
    @return: un numero o lista de numeros con el resultado de las llamadas a set_infoLabels_item
    @rtype: int, list
    """
    start_time = time.time()

    if type(source) == list:
        ret = set_infoLabels_itemlist(source, seekTmdb, idioma_busqueda)
        logger.debug("Se han obtenido los datos de %i enlaces en %f segundos" % (len(source), time.time() - start_time))
    else:
        ret = set_infoLabels_item(source, seekTmdb, idioma_busqueda)
        logger.debug("Se han obtenido los datos del enlace en %f segundos" % (time.time() - start_time))
    return ret


def infoLabels_tostring(item, separador="\n"):
    """
    Retorna un str con la lista ordenada con los infoLabels del item

    @param item: item
    @type item: item
    @param separador: tipo de separador de los campos
    @type separador: str
    @return: la lista ordenada con los infoLabels del item
    @rtype: str
    """
    return separador.join([var + "= " + str(item.infoLabels[var]) for var in sorted(item.infoLabels)])


# ---------------------------------------------------------------------------------------------------------------
# class Tmdb:
#   Scraper para streamondemand basado en el Api de https://www.themoviedb.org/
#   version 1.4:
#       - Documentada limitacion de uso de la API (ver mas abajo).
#       - Añadido metodo get_temporada()
#   version 1.3:
#       - Corregido error al devolver None el path_poster y el backdrop_path
#       - Corregido error que hacia que en el listado de generos se fueran acumulando de una llamada a otra
#       - Añadido metodo get_generos()
#       - Añadido parametros opcional idioma_alternativo al metodo get_sinopsis()
#
#
#   Uso:
#   Metodos constructores:
#    Tmdb(texto_buscado, tipo)
#        Parametros:
#            texto_buscado:(str) Texto o parte del texto a buscar
#            tipo: ("movie" o "tv") Tipo de resultado buscado peliculas o series. Por defecto "movie"
#            (opcional) idioma_busqueda: (str) codigo del idioma segun ISO 639-1
#            (opcional) include_adult: (bool) Se incluyen contenidos para adultos en la busqueda o no. Por defecto
# 'False'
#            (opcional) year: (str) Año de lanzamiento.
#            (opcional) page: (int) Cuando hay muchos resultados para una busqueda estos se organizan por paginas.
#                            Podemos cargar la pagina que deseemos aunque por defecto siempre es la primera.
#        Return:
#            Esta llamada devuelve un objeto Tmdb que contiene la primera pagina del resultado de buscar 'texto_buscado'
#            en la web themoviedb.org. Cuantos mas parametros opcionales se incluyan mas precisa sera la busqueda.
#            Ademas el objeto esta inicializado con el primer resultado de la primera pagina de resultados.
#    Tmdb(id_Tmdb,tipo)
#       Parametros:
#           id_Tmdb: (str) Codigo identificador de una determinada pelicula o serie en themoviedb.org
#           tipo: ("movie" o "tv") Tipo de resultado buscado peliculas o series. Por defecto "movie"
#           (opcional) idioma_busqueda: (str) codigo del idioma segun ISO 639-1
#       Return:
#           Esta llamada devuelve un objeto Tmdb que contiene el resultado de buscar una pelicula o serie con el
# identificador id_Tmd
#           en la web themoviedb.org.
#    Tmdb(external_id, external_source, tipo)
#       Parametros:
#           external_id: (str) Codigo identificador de una determinada pelicula o serie en la web referenciada por
# 'external_source'.
#           external_source: (Para series:"imdb_id","freebase_mid","freebase_id","tvdb_id","tvrage_id"; Para
# peliculas:"imdb_id")
#           tipo: ("movie" o "tv") Tipo de resultado buscado peliculas o series. Por defecto "movie"
#           (opcional) idioma_busqueda: (str) codigo del idioma segun ISO 639-1
#       Return:
#           Esta llamada devuelve un objeto Tmdb que contiene el resultado de buscar una pelicula o serie con el
# identificador 'external_id' de
#           la web referenciada por 'external_source' en la web themoviedb.org.
#
#   Metodos principales:
#    get_id(): Retorna un str con el identificador Tmdb de la pelicula o serie cargada o una cadena vacia si no hubiese
# nada cargado.
#    get_sinopsis(idioma_alternativo): Retorna un str con la sinopsis de la serie o pelicula cargada.
#    get_poster (tipo_respuesta,size): Obtiene el poster o un listado de posters.
#    get_backdrop (tipo_respuesta,size): Obtiene una imagen de fondo o un listado de imagenes de fondo.
#    get_fanart (tipo,idioma,temporada): Obtiene un listado de imagenes del tipo especificado de la web Fanart.tv
#    get_temporada(temporada): Obtiene un diccionario con datos especificos de la temporada.
#    get_episodio (temporada, capitulo): Obtiene un diccionario con datos especificos del episodio.
#    get_generos(): Retorna un str con la lista de generos a los que pertenece la pelicula o serie.
#
#
#   Otros metodos:
#    load_resultado(resultado, page): Cuando la busqueda devuelve varios resultados podemos seleccionar que resultado
# concreto y de que pagina cargar los datos.
#
#   Limitaciones:
#   El uso de la API impone un limite de 20 conexiones simultaneas (concurrencia) o 30 peticiones en 10 segundos por IP
# Informacion sobre la api : http://docs.themoviedb.apiary.io
# -------------------------------------------------------------------------------------------------------------------


class Tmdb(object):
    # Atributo de clase
    dic_generos = {}
    '''
    dic_generos={"id_idioma1": {"tv": {"id1": "name1",
                                       "id2": "name2"
                                      },
                                "movie": {"id1": "name1",
                                          "id2": "name2"
                                          }
                                }
                }
    '''

    def __search(self, index_resultado=0, page=1):
        # http://api.themoviedb.org/3/search/movie?api_key=f7f51775877e0bb6703520952b3c7840&query=superman&language=es
        # &include_adult=false&page=1
        url = ('http://api.themoviedb.org/3/search/%s?api_key=f7f51775877e0bb6703520952b3c7840&query=%s&language=%s'
               '&include_adult=%s&page=%s' % (self.busqueda["tipo"], self.busqueda["texto"].replace(' ', '%20'),
                                              self.busqueda["idioma"], self.busqueda["include_adult"], str(page)))
        if self.busqueda["year"] != '':
            url += '&year=' + str(self.busqueda["year"])

        buscando = self.busqueda["texto"].capitalize()
        logger.info("[Tmdb.py] Buscando %s en pagina %s:\n%s" % (buscando, page, url))

        response_dic = {}
        try:
            response_dic = jsontools.load_json(scrapertools.downloadpageWithoutCookies(url))
            self.total_results = response_dic["total_results"]
            self.total_pages = response_dic["total_pages"]
        except:
            self.total_results = 0

        if self.total_results > 0:
            self.results = response_dic["results"]

        if len(self.results) > 0:
            if self.busqueda['filtro']:
                # TODO documentar esta parte
                for key, value in dict(self.busqueda['filtro']).items():
                    for r in self.results[:]:
                        '''  # Opcion mas permisiva
                        if r.has_key(k) and r[k] != v:
                            self.results.remove(r)
                            self.total_results -= 1
                        '''
                        # Opcion mas precisa
                        if key not in r or r[key] != value:
                            self.results.remove(r)
                            self.total_results -= 1

            if index_resultado < len(self.results):
                self.__leer_resultado(self.results[index_resultado])
            else:
                logger.error("La busqueda de '{0}' no dio {1} resultados para la pagina {2}"
                             .format(buscando, index_resultado + 1, page))
        else:
            # No hay resultados de la busqueda
            logger.error("La busqueda de '%s' no dio resultados para la pagina %s" % (buscando, page))

    def __by_id(self, source="tmdb"):

        if source == "tmdb":
            # http://api.themoviedb.org/3/movie/1924?api_key=f7f51775877e0bb6703520952b3c7840&language=es
            # &append_to_response=images,videos,external_ids,credits&include_image_language=es,null
            # http://api.themoviedb.org/3/tv/1407?api_key=f7f51775877e0bb6703520952b3c7840&language=es
            # &append_to_response=images,videos,external_ids,credits&include_image_language=es,null
            url = ('http://api.themoviedb.org/3/%s/%s?api_key=f7f51775877e0bb6703520952b3c7840&language=%s'
                   '&append_to_response=images,videos,external_ids,credits&include_image_language=%s,null' %
                   (self.busqueda["tipo"], self.busqueda["id"], self.busqueda["idioma"], self.busqueda["idioma"]))
            buscando = "id_Tmdb: " + self.busqueda["id"]

        else:
            # http://api.themoviedb.org/3/find/%s?external_source=imdb_id&api_key=f7f51775877e0bb6703520952b3c7840
            url = ('http://api.themoviedb.org/3/find/%s?external_source=%s&api_key=f7f51775877e0bb6703520952b3c7840'
                   '&language=%s' % (self.busqueda["id"], source, self.busqueda["idioma"]))
            buscando = source.capitalize() + ": " + self.busqueda["id"]

        logger.info("[Tmdb.py] Buscando %s:\n%s" % (buscando, url))
        try:
            resultado = jsontools.load_json(scrapertools.downloadpageWithoutCookies(url))

            if source != "tmdb":
                if self.busqueda["tipo"] == "movie":
                    resultado = resultado["movie_results"]
                else:
                    resultado = resultado["tv_results"]
                if len(resultado) > 0:
                    resultado = resultado[0]
        except:
            resultado = {}

        if len(resultado) > 0:
            self.result = resultado
            if self.total_results == 0:
                self.results.append(resultado)
                self.total_results = 1
                self.total_pages = 1

            self.__leer_resultado(resultado)

        else:  # No hay resultados de la busqueda
            logger.debug("La busqueda de %s no dio resultados." % buscando)


    def __inicializar(self):
        # Inicializamos las colecciones de resultados, fanart y temporada
        for i in (self.result, self.fanart, self.temporada):
            for k in i.keys():
                if type(i[k]) == str:
                    i[k] = ""
                elif type(i[k]) == list:
                    i[k] = []
                elif type(i[k]) == dict:
                    i[k] = {}

    def __init__(self, **kwargs):
        self.page = kwargs.get('page', 1)
        self.results = []
        self.total_pages = 0
        self.total_results = 0
        self.fanart = {}
        self.temporada = {}

        self.busqueda = {'id': "",
                         'texto': "",
                         'tipo': kwargs.get('tipo', 'movie'),
                         'idioma': kwargs.get('idioma_busqueda', 'es'),
                         'include_adult': str(kwargs.get('include_adult', 'false')),
                         'year': kwargs.get('year', ''),
                         'filtro': kwargs.get('filtro', {})
                         }

        self.result = {'adult': "",
                       'backdrop_path': "",  # ruta imagen de fondo mas valorada
                       # belongs_to_collection
                       'budget': "",  # Presupuesto
                       'genres': [],  # lista de generos
                       'homepage': "",
                       'id': "", 'imdb_id': "", 'freebase_mid': "", 'freebase_id': "", 'tvdb_id': "", 'tvrage_id': "",
                       # IDs equivalentes
                       'original_language': "",
                       'original_title': "",
                       'overview': "",  # sinopsis
                       # popularity
                       'poster_path': "",
                       'production_companies': [],
                       'production_countries': [],
                       'origin_country': [],
                       'release_date': "",
                       'first_air_date': "",
                       'revenue': "",  # recaudacion
                       'runtime': "",  # runtime duracion
                       # spoken_languages
                       'status': "",
                       'tagline': "",
                       'title': "",
                       'video': "",  # ("true" o "false") indica si la busqueda movies/id/videos devolvera algo o no
                       'vote_average': "",
                       'vote_count': "",
                       'name': "",  # nombre en caso de personas o series (tv)
                       'profile_path': "",  # ruta imagenes en caso de personas
                       'known_for': {},  # Diccionario de peliculas en caso de personas (id_pelicula:titulo)
                       'images_backdrops': [],
                       'images_posters': [],
                       'images_profiles': [],
                       'videos': []
                       }

        def rellenar_dic_generos():
            # Rellenar diccionario de generos del tipo e idioma seleccionados
            if self.busqueda["idioma"] not in Tmdb.dic_generos:
                Tmdb.dic_generos[self.busqueda["idioma"]] = {}
            if self.busqueda["tipo"] not in Tmdb.dic_generos[self.busqueda["idioma"]]:
                Tmdb.dic_generos[self.busqueda["idioma"]][self.busqueda["tipo"]] = {}
            url = ('http://api.themoviedb.org/3/genre/%s/list?api_key=f7f51775877e0bb6703520952b3c7840&language=%s'
                   % (self.busqueda["tipo"], self.busqueda["idioma"]))
            try:
                lista_generos = jsontools.load_json(scrapertools.downloadpageWithoutCookies(url))["genres"]
            except:
                pass
            for i in lista_generos:
                Tmdb.dic_generos[self.busqueda["idioma"]][self.busqueda["tipo"]][str(i["id"])] = i["name"]

        if self.busqueda["tipo"] == 'movie' or self.busqueda["tipo"] == "tv":
            if self.busqueda["idioma"] not in Tmdb.dic_generos:
                rellenar_dic_generos()
            elif self.busqueda["tipo"] not in Tmdb.dic_generos[self.busqueda["idioma"]]:
                rellenar_dic_generos()
        else:
            # La busqueda de personas no esta soportada en esta version.
            raise Exception("Parametros no validos al crear el objeto Tmdb.\nConsulte los modos de uso.")

        if 'id_Tmdb' in kwargs:
            self.busqueda["id"] = kwargs.get('id_Tmdb')
            self.__by_id()
        elif 'texto_buscado' in kwargs:
            self.busqueda["texto"] = kwargs.get('texto_buscado')
            self.__search(page=self.page)
        elif 'external_source' in kwargs and 'external_id' in kwargs:
            # TV Series: imdb_id, freebase_mid, freebase_id, tvdb_id, tvrage_id
            # Movies: imdb_id
            if (self.busqueda["tipo"] == 'movie' and kwargs.get('external_source') == "imdb_id") or \
                    (self.busqueda["tipo"] == 'tv' and kwargs.get('external_source') in (
                            "imdb_id", "freebase_mid", "freebase_id", "tvdb_id", "tvrage_id")):
                self.busqueda["id"] = kwargs.get('external_id')
                self.__by_id(source=kwargs.get('external_source'))
        else:
            raise Exception("Parametros no validos al crear el objeto Tmdb.\nConsulte los modos de uso.")

    def __leer_resultado(self, data):
        for k, v in data.items():
            if k == "genre_ids":  # Lista de generos (lista con los id de los generos)
                self.result["genres"] = []
                for i in v:
                    try:
                        self.result["genres"].append(
                            self.dic_generos[self.busqueda["idioma"]][self.busqueda["tipo"]][str(i)])
                    except:
                        pass
            elif k == "genre" or k == "genres":  # Lista  de generos (lista de objetos {id,nombre})
                self.result["genres"] = []
                for i in v:
                    self.result["genres"].append(i['name'])

            elif k == "known_for":  # Lista de peliculas de un actor
                for i in v:
                    self.result["known_for"][i['id']] = i['title']

            elif k == "images":  # Se incluyen los datos de las imagenes
                if "backdrops" in v:
                    self.result["images_backdrops"] = v["backdrops"]
                if "posters" in v:
                    self.result["images_posters"] = v["posters"]
                if "profiles" in v:
                    self.result["images_profiles"] = v["profiles"]

            elif k == "credits":  # Se incluyen los creditos
                if "cast" in v:
                    self.result["credits_cast"] = v["cast"]
                if "crew" in v:
                    self.result["credits_crew"] = v["crew"]

            elif k == "videos":  # Se incluyen los datos de los videos
                self.result["videos"] = v["results"]

            elif k == "external_ids":  # Listado de IDs externos
                for kj, _id in v.items():
                    # print kj + ":" + str(id)
                    if kj in self.result:
                        self.result[kj] = str(_id)

            elif k in self.result:  # el resto
                if type(v) == list or type(v) == dict:
                    self.result[k] = v
                elif v is None:
                    self.result[k] = ""
                else:
                    self.result[k] = str(v)

    def load_resultado(self, index_resultado=0, page=1):
        # Si no hay mas de un resultado no podemos cambiar
        if self.total_results <= 1:
            return None

        if page < 1 or page > self.total_pages:
            page = 1
        if index_resultado < 0:
            index_resultado = 0

        self.__inicializar()
        if page != self.page:
            self.__search(index_resultado=index_resultado, page=page)
            self.page = page
        else:
            # print self.result["genres"]
            self.__leer_resultado(self.results[index_resultado])

    def get_list_resultados(self, numResult=20):
        # TODO documentar
        res = []

        numResult = numResult if numResult > 0 else self.total_results
        numResult = min([numResult, self.total_results])

        cr = 0
        for p in range(1, self.total_pages + 1):
            for r in range(0, len(self.results)):
                try:
                    self.load_resultado(r, p)
                    self.result['type'] = self.busqueda.get("tipo", "movie")
                    self.result['thumbnail'] = self.get_poster(size="w300")
                    self.result['fanart'] = self.get_backdrop()
                    res.append(self.result.copy())
                    cr += 1
                    if cr >= numResult:
                        return res
                except:
                    continue
        return res

    def get_generos(self):
        # --------------------------------------------------------------------------------------------------------------------------------------------
        #   Parametros:
        #       none
        #   Return: (str)
        #       Devuelve la lista de generos a los que pertenece la pelicula o serie.
        # --------------------------------------------------------------------------------------------------------------------------------------------
        return ', '.join(self.result["genres"])

    def get_id(self):
        """

        :return: Devuelve el identificador Tmdb de la pelicula o serie cargada o una cadena vacia en caso de que no
            hubiese nada cargado. Se puede utilizar este metodo para saber si una busqueda ha dado resultado o no.
        :rtype: str
        """
        return str(self.result['id'])

    def get_sinopsis(self, idioma_alternativo=""):
        """

        :param idioma_alternativo: codigo del idioma, segun ISO 639-1, en el caso de que en el idioma fijado para la
            busqueda no exista sinopsis.
            Por defecto, se utiliza el idioma original. Si se utiliza None como idioma_alternativo, solo se buscara en
            el idioma fijado.
        :type idioma_alternativo: str
        :return: Devuelve la sinopsis de una pelicula o serie
        :rtype: str
        """
        ret = ""
        if self.result['id']:
            ret = self.result['overview']
            if self.result['overview'] == "" and str(idioma_alternativo).lower() != 'none':
                # Vamos a lanzar una busqueda por id y releer de nuevo la sinopsis
                self.busqueda["id"] = str(self.result["id"])
                if idioma_alternativo:
                    self.busqueda["idioma"] = idioma_alternativo
                else:
                    self.busqueda["idioma"] = self.result['original_language']
                url = ('http://api.themoviedb.org/3/%s/%s?api_key=f7f51775877e0bb6703520952b3c7840&language=%s' %
                       (self.busqueda["tipo"], self.busqueda["id"], self.busqueda["idioma"]))
                try:
                    resultado = jsontools.load_json(scrapertools.downloadpageWithoutCookies(url))
                except:
                    pass

                if resultado:
                    if 'overview' in resultado:
                        self.result['overview'] = resultado['overview']
                        ret = self.result['overview']
        return ret

    def get_poster(self, tipo_respuesta="str", size="original"):
        """

        @param tipo_respuesta: Tipo de dato devuelto por este metodo. Por defecto "str"
        @type tipo_respuesta: list, str
        @param size: ("w45", "w92", "w154", "w185", "w300", "w342", "w500", "w600", "h632", "w780", "w1280", "original")
            Indica la anchura(w) o altura(h) de la imagen a descargar. Por defecto "original"
        @return: Si el tipo_respuesta es "list" devuelve un listado con todas las urls de las imagenes tipo poster del
            tamaño especificado.
            Si el tipo_respuesta es "str" devuelve la url de la imagen tipo poster, mas valorada, del tamaño
            especificado.
            Si el tamaño especificado no existe se retornan las imagenes al tamaño original.
        @rtype: list, str
        """
        ret = []
        if size not in ("w45", "w92", "w154", "w185", "w300", "w342", "w500", "w600", "h632", "w780", "w1280",
                        "original"):
            size = "original"

        if self.result["poster_path"] is None or self.result["poster_path"] == "":
            poster_path = ""
        else:
            poster_path = 'http://image.tmdb.org/t/p/' + size + self.result["poster_path"]

        if tipo_respuesta == 'str':
            return poster_path
        elif self.result["id"] == "":
            return []

        if len(self.result['images_posters']) == 0:
            # Vamos a lanzar una busqueda por id y releer de nuevo todo
            self.busqueda["id"] = str(self.result["id"])
            self.__by_id()

        if len(self.result['images_posters']) > 0:
            for i in self.result['images_posters']:
                imagen_path = i['file_path']
                if size != "original":
                    # No podemos pedir tamaños mayores que el original
                    if size[1] == 'w' and int(imagen_path['width']) < int(size[1:]):
                        size = "original"
                    elif size[1] == 'h' and int(imagen_path['height']) < int(size[1:]):
                        size = "original"
                ret.append('http://image.tmdb.org/t/p/' + size + imagen_path)
        else:
            ret.append(poster_path)

        return ret

    def get_backdrop(self, tipo_respuesta="str", size="original"):
        """
        Devuelve las imagenes de tipo backdrop
        @param tipo_respuesta: Tipo de dato devuelto por este metodo. Por defecto "str"
        @type tipo_respuesta: list, str
        @param size: ("w45", "w92", "w154", "w185", "w300", "w342", "w500", "w600", "h632", "w780", "w1280", "original")
            Indica la anchura(w) o altura(h) de la imagen a descargar. Por defecto "original"
        @type size: str
        @return: Si el tipo_respuesta es "list" devuelve un listado con todas las urls de las imagenes tipo backdrop del
            tamaño especificado.
        Si el tipo_respuesta es "str" devuelve la url de la imagen tipo backdrop, mas valorada, del tamaño especificado.
        Si el tamaño especificado no existe se retornan las imagenes al tamaño original.
        @rtype: list, str
        """
        ret = []
        if size not in ("w45", "w92", "w154", "w185", "w300", "w342", "w500", "w600", "h632", "w780", "w1280",
                        "original"):
            size = "original"

        if self.result["backdrop_path"] is None or self.result["backdrop_path"] == "":
            backdrop_path = ""
        else:
            backdrop_path = 'http://image.tmdb.org/t/p/' + size + self.result["backdrop_path"]

        if tipo_respuesta == 'str':
            return backdrop_path
        elif self.result["id"] == "":
            return []

        if len(self.result['images_backdrops']) == 0:
            # Vamos a lanzar una busqueda por id y releer de nuevo todo
            self.busqueda["id"] = str(self.result["id"])
            self.__by_id()

        if len(self.result['images_backdrops']) > 0:
            for i in self.result['images_backdrops']:
                imagen_path = i['file_path']
                if size != "original":
                    # No podemos pedir tamaños mayores que el original
                    if size[1] == 'w' and int(imagen_path['width']) < int(size[1:]):
                        size = "original"
                    elif size[1] == 'h' and int(imagen_path['height']) < int(size[1:]):
                        size = "original"
                ret.append('http://image.tmdb.org/t/p/' + size + imagen_path)
        else:
            ret.append(backdrop_path)

        return ret

    def get_fanart(self, tipo="hdclearart", idioma=None, temporada="all"):
        """

        @param tipo: ("hdclearlogo", "poster",	"banner", "thumbs",	"hdclearart", "clearart", "background",	"clearlogo",
            "characterart", "seasonthumb", "seasonposter", "seasonbanner", "moviedisc")
            Indica el tipo de Art que se desea obtener, segun la web Fanart.tv. Alguno de estos tipos pueden estar solo
            disponibles para peliculas o series segun el caso. Por defecto "hdclearart"
        @type tipo: str
        @param idioma: (opcional) Codigos del idioma segun ISO 639-1, "all" (por defecto) para todos los idiomas o "00"
            para ninguno. Por ejemplo: idioma=["es","00","en"] Incluiria los resultados en español, sin idioma definido
            y en ingles, en este orden.
        @type idioma: list
        @param temporada: (opcional solo para series) Un numero entero que representa el numero de temporada, el numero
            cero para especiales o "all" para imagenes validas para cualquier temporada. Por defecto "all".
        @type: temporada: str
        @return: Retorna una lista con las url de las imagenes segun los parametros de entrada y ordenadas segun las
            votaciones de Fanart.tv
        @rtype: list

        """
        if idioma is None:
            idioma = ["all"]

        if self.result["id"] == "":
            return []

        if len(self.fanart) == 0:  # Si esta vacio acceder a Fanart.tv y cargar el resultado
            if self.busqueda['tipo'] == 'movie':
                # http://assets.fanart.tv/v3/movies/1924?api_key=dffe90fba4d02c199ae7a9e71330c987
                url = "http://assets.fanart.tv/v3/movies/" + str(
                    self.result["id"]) + "?api_key=dffe90fba4d02c199ae7a9e71330c987"
                temporada = ""
            elif self.busqueda['tipo'] == 'tv':
                # En este caso necesitamos el tvdb_id
                if self.result["tvdb_id"] == '':
                    # Vamos lanzar una busqueda por id y releer de nuevo todo
                    self.busqueda["id"] = str(self.result["id"])
                    self.__by_id()

                # http://assets.fanart.tv/v3/tv/153021?api_key=dffe90fba4d02c199ae7a9e71330c987
                url = "http://assets.fanart.tv/v3/tv/" + str(
                    self.result["tvdb_id"]) + "?api_key=dffe90fba4d02c199ae7a9e71330c987"
            else:
                # 'person' No soportado
                return None

            fanarttv = jsontools.load_json(scrapertools.downloadpageWithoutCookies(url))
            if fanarttv is None:  # Si el item buscado no esta en Fanart.tv devolvemos una lista vacia
                return []

            for k, v in fanarttv.items():
                if k in ("hdtvlogo", "hdmovielogo"):
                    self.fanart["hdclearlogo"] = v
                elif k in ("tvposter", "movieposter"):
                    self.fanart["poster"] = v
                elif k in ("tvbanner", "moviebanner"):
                    self.fanart["banner"] = v
                elif k in ("tvthumb", "moviethumb"):
                    self.fanart["thumbs"] = v
                elif k in ("hdclearart", "hdmovieclearart"):
                    self.fanart["hdclearart"] = v
                elif k in ("clearart", "movieart"):
                    self.fanart["clearart"] = v
                elif k in ("showbackground", "moviebackground"):
                    self.fanart["background"] = v
                elif k in ("clearlogo", "movielogo"):
                    self.fanart["clearlogo"] = v
                elif k in ("characterart", "seasonthumb", "seasonposter", "seasonbanner", "moviedisc"):
                    self.fanart[k] = v

        # inicializamos el diccionario con los idiomas
        ret_dic = {}
        for i in idioma:
            ret_dic[i] = []

        for i in self.fanart[tipo]:
            if i["lang"] in idioma:
                if "season" not in i:
                    ret_dic[i["lang"]].append(i["url"])
                elif temporada == "" or (temporada == 'all' and i["season"] == 'all'):
                    ret_dic[i["lang"]].append(i["url"])
                else:
                    if i["season"] == "":
                        i["season"] = 0
                    else:
                        i["season"] = int(i["season"])
                    if i["season"] == int(temporada):
                        ret_dic[i["lang"]].append(i["url"])
            elif "all" in idioma:
                ret_dic["all"].append(i["url"])

        ret_list = []
        for i in idioma:
            ret_list.extend(ret_dic[i])

        # print ret_list
        return ret_list

    def get_episodio(self, numtemporada=1, capitulo=1):
        # --------------------------------------------------------------------------------------------------------------------------------------------
        #   Parametros:
        #       numtemporada(opcional): (int) Numero de temporada. Por defecto 1.
        #       capitulo: (int) Numero de capitulo. Por defecto 1.
        #   Return: (dic)
        #       Devuelve un dicionario con los siguientes elementos:
        #           "temporada_nombre", "temporada_sinopsis", "temporada_poster", "temporada_num_episodios"(int),
        #           "episodio_titulo", "episodio_sinopsis", "episodio_imagen", "episodio_air_date", "episodio_air_date",
        #           "episodio_crew", "episodio_guest_stars", "episodio_vote_count" y "episodio_vote_average"
        # --------------------------------------------------------------------------------------------------------------------------------------------
        if self.result["id"] == "" or self.busqueda["tipo"] != "tv":
            return {}

        capitulo = int(capitulo)
        if capitulo < 1:
            capitulo = 1

        temporada = self.get_temporada(numtemporada)
        if not temporada:
            # Se ha producido un error
            return {}
        if len(temporada["episodes"]) < capitulo:
            # Se ha producido un error
            logger.error("Episodio %d de la temporada %d no encontrado." % (capitulo, numtemporada))
            return {}

        ret_dic = dict()
        ret_dic["temporada_nombre"] = temporada["name"]
        ret_dic["temporada_sinopsis"] = temporada["overview"]
        ret_dic["temporada_poster"] = ('http://image.tmdb.org/t/p/original' + temporada["poster_path"]) if temporada[
            "poster_path"] else ""
        ret_dic["temporada_num_episodios"] = len(temporada["episodes"])

        episodio = temporada["episodes"][capitulo - 1]
        ret_dic["episodio_titulo"] = episodio["name"]
        ret_dic["episodio_sinopsis"] = episodio["overview"]
        ret_dic["episodio_imagen"] = ('http://image.tmdb.org/t/p/original' + episodio["still_path"]) if episodio[
            "still_path"] else ""

        ret_dic["episodio_air_date"] = episodio["air_date"]
        ret_dic["episodio_crew"] = episodio["crew"]
        ret_dic["episodio_guest_stars"] = episodio["guest_stars"]
        ret_dic["episodio_vote_count"] = episodio["vote_count"]
        ret_dic["episodio_vote_average"] = episodio["vote_average"]
        return ret_dic

    def get_temporada(self, numtemporada=1):
        # --------------------------------------------------------------------------------------------------------------------------------------------
        #   Parametros:
        #       numtemporada: (int) Numero de temporada. Por defecto 1.
        #   Return: (dic)
        #       Devuelve un dicionario con datos sobre la temporada.
        #       Puede obtener mas informacion sobre los datos devueltos en:
        #           http://docs.themoviedb.apiary.io/#reference/tv-seasons/tvidseasonseasonnumber/get
        #           http://docs.themoviedb.apiary.io/#reference/tv-seasons/tvidseasonseasonnumbercredits/get
        # --------------------------------------------------------------------------------------------------------------------------------------------
        if self.result["id"] == "" or self.busqueda["tipo"] != "tv":
            return {}

        numtemporada = int(numtemporada)
        if numtemporada < 0:
            numtemporada = 1

        # if not self.temporada.has_key("season_number") or self.temporada["season_number"] != numtemporada:
        # if numtemporada > len(self.temporada) or self.temporada[numtemporada] is None:
        if not self.temporada.has_key(numtemporada) or not self.temporada[numtemporada]:
            # Si no hay datos sobre la temporada solicitada, consultar en la web

            # http://api.themoviedb.org/3/tv/1407/season/1?api_key=f7f51775877e0bb6703520952b3c7840&language=es&
            # append_to_response=credits
            url = "http://api.themoviedb.org/3/tv/%s/season/%s?api_key=f7f51775877e0bb6703520952b3c7840&language=%s" \
                  "&append_to_response=credits" % (self.result["id"], numtemporada, self.busqueda["idioma"])

            buscando = "id_Tmdb: " + str(self.result["id"]) + " temporada: " + str(numtemporada) + "\nURL: " + url
            logger.info("[Tmdb.py] Buscando " + buscando)

            try:
                self.temporada[numtemporada] = jsontools.load_json(scrapertools.downloadpageWithoutCookies(url))
            except:
                self.temporada[numtemporada] = ["status_code"]

            if "status_code" in self.temporada[numtemporada]:
                # Se ha producido un error
                self.temporada[numtemporada] = {}
                logger.error("La busqueda de " + buscando + " no dio resultados.")
                return {}

        return self.temporada[numtemporada]

    def get_videos(self):
        """
        :return: Devuelve una lista ordenada (idioma/resolucion/tipo) de objetos Dict en la que cada uno de
        sus elementos corresponde con un trailer, teaser o clip de youtube.
        :rtype: list of Dict
        """
        ret = []
        if self.result['id']:
            if not self.result['videos']:
                # Primera búsqueda de videos en el idioma de busqueda
                url = "http://api.themoviedb.org/3/%s/%s/videos?api_key=f7f51775877e0bb6703520952b3c7840&language=%s" \
                      % (self.busqueda['tipo'], self.result['id'], self.busqueda["idioma"])
                try:
                    dict_videos = jsontools.load_json(scrapertools.downloadpageWithoutCookies(url))
                except:
                    pass

                if dict_videos['results']:
                    dict_videos['results'] = sorted(dict_videos['results'], key=lambda x: (x['type'], x['size']))
                    self.result["videos"] = dict_videos['results']

            # Si el idioma de busqueda no es ingles, hacer una segunda búsqueda de videos en inglés
            if self.busqueda["idioma"] != 'en':
                url = "http://api.themoviedb.org/3/%s/%s/videos?api_key=f7f51775877e0bb6703520952b3c7840" \
                      % (self.busqueda['tipo'], self.result['id'])
                try:
                    dict_videos = jsontools.load_json(scrapertools.downloadpageWithoutCookies(url))
                except:
                    pass

                if dict_videos['results']:
                    dict_videos['results'] = sorted(dict_videos['results'], key=lambda x: (x['type'], x['size']))
                    self.result["videos"].extend(dict_videos['results'])

            # Si las busqueda han obtenido resultados devolver un listado de objetos
            for i in self.result['videos']:
                if i['site'] == "YouTube":
                    ret.append({'name': i['name'],
                                'url': "https://www.youtube.com/watch?v=%s" % i['key'],
                                'size': str(i['size']),
                                'type': i['type'],
                                'language': i['iso_639_1']})

        return ret

    def get_infoLabels(self, infoLabels=None, origen=None):
        """
        :param infoLabels: Informacion extra de la pelicula, serie, temporada o capitulo.
        :type infoLabels: Dict
        :return: Devuelve la informacion extra obtenida del objeto actual. Si se paso el parametro infoLables, el valor
        devuelto sera el leido como parametro debidamente actualizado.
        :rtype: Dict
        """
        ret_infoLabels = copy.copy(infoLabels) if infoLabels else {}
        items = self.result.items() if not origen else origen.items()

        for k, v in items:
            if v == '':
                continue
            elif type(v) == str:
                v = re.sub(r"\n|\r|\t", "", v)

            if k == 'overview':
                ret_infoLabels['plot'] = self.get_sinopsis()
            elif k == 'runtime':
                ret_infoLabels['duration'] = v
            elif k == 'release_date':
                ret_infoLabels['year'] = int(v[:4])
            elif k == 'first_air_date':
                ret_infoLabels['year'] = int(v[:4])
                ret_infoLabels['aired'] = v
                ret_infoLabels['premiered'] = v
            elif k == 'original_title':
                ret_infoLabels['originaltitle'] = v
            elif k == 'vote_average':
                ret_infoLabels['rating'] = float(v)
            elif k == 'vote_count':
                ret_infoLabels['votes'] = v
            elif k == 'poster_path':
                ret_infoLabels['thumbnail'] = 'http://image.tmdb.org/t/p/original' + v
            elif k == 'backdrop_path':
                ret_infoLabels['fanart'] = 'http://image.tmdb.org/t/p/original' + v
            elif k == 'id':
                ret_infoLabels['tmdb_id'] = v
            elif k == 'imdb_id':
                ret_infoLabels['imdb_id'] = v
                ret_infoLabels['IMDBNumber'] = v
                ret_infoLabels['code'] = v
            elif k == 'genres':
                ret_infoLabels['genre'] = self.get_generos()
            elif k == 'name':
                ret_infoLabels['title'] = v
            elif k == 'production_companies':
                ret_infoLabels['studio'] = ", ".join(i['name'] for i in v)
            elif k == 'production_countries' or k == 'origin_country':
                if 'country' not in ret_infoLabels:
                    ret_infoLabels['country'] = ", ".join(i if type(i) == str else i['name'] for i in v)
                else:
                    ret_infoLabels['country'] = ", " + ", ".join(i if type(i) == str else i['name'] for i in v)
            elif k == 'credits_cast':
                ret_infoLabels['castandrole'] = []
                for c in sorted(v, key=lambda c: c.get("order")):
                    ret_infoLabels['castandrole'].append((c['name'], c['character']))
            elif k == 'credits_crew':
                l_director = []
                l_writer = []
                for crew in v:
                    if crew['job'].lower() == 'director':
                        l_director.append(crew['name'])
                    elif crew['job'].lower() in ('screenplay', 'writer'):
                        l_writer.append(crew['name'])
                if l_director:
                    ret_infoLabels['director'] = ", ".join(l_director)
                if l_writer:
                    if 'writer' not in ret_infoLabels:
                        ret_infoLabels['writer'] = ", ".join(l_writer)
                    else:
                        ret_infoLabels['writer'] += "," + (",".join(l_writer))
            elif k == 'created_by':
                l_writer = []
                for cr in v:
                    l_writer.append(cr['name'])
                if 'writer' not in ret_infoLabels:
                    ret_infoLabels['writer'] = ",".join(l_writer)
                else:
                    ret_infoLabels['writer'] += "," + (",".join(l_writer))
            elif k == 'videos' and len(v) > 0:
                if v[0]["site"] == "YouTube":
                    ret_infoLabels['trailer'] = "https://www.youtube.com/watch?v=" + v[0]["key"]
            elif type(v) == str:
                ret_infoLabels[k] = v
                # logger.debug(k +'= '+ v)

        return ret_infoLabels


####################################################################################################
#   for StreamOnDemand by costaplus
# ====================================================================================================
def infoSod(item, tipo="movie"):
    '''
    :param item:  item
    :return:      ritorna un'item completo esente da errori di codice
    '''
    logger.info("streamondemand.core.tmdb infoSod")
    logger.info("channel=[" + item.channel + "], action=[" + item.action + "], title[" + item.title + "], url=[" + item.url + "], thumbnail=[" + item.thumbnail + "], tipo=[" + tipo + "]")
    try:
        tmdbtitle = item.fulltitle.split("|")[0].split("{")[0].split("[")[0].split("(")[0].split("Sub-ITA")[0].split("Sub ITA")[0].split("20")[0].split("19")[0].split("S0")[0].split("Serie")[0].split("HD ")[0]
        year = scrapertools.find_single_match(item.fulltitle, '\((\d{4})\)')

        otmdb = Tmdb(texto_buscado=tmdbtitle,
                     tipo=tipo,
                     idioma_busqueda='it',
                     year=year)

        item.infoLabels = otmdb.get_infoLabels()
        if 'thumbnail' in item.infoLabels:
            item.thumbnail = item.infoLabels['thumbnail']
        if 'fanart' in item.infoLabels:
            item.fanart = item.infoLabels['fanart']

    except:
        pass
    return item

# ===================================================================================================

