# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# Ricerca "buscadorall"
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------
import Queue
import datetime
import glob
import os
import re
import time
import urllib
from threading import Thread
from unicodedata import normalize

import xbmc

from core import channeltools
from core import scrapertools
from lib.fuzzywuzzy import fuzz
from platformcode import platformtools

try:
    import json
except:
    import simplejson as json

from core import config
from core import logger
from core.item import Item

__channel__ = "buscadorall"
__category__ = "F"
__type__ = "generic"
__title__ = "buscadorall"
__language__ = "IT"

host = "http://www.ibs.it"

DEBUG = config.get_setting("debug")

TMDB_KEY = 'f7f51775877e0bb6703520952b3c7840'
#try:
#    TMDBaddon = xbmcaddon.Addon('metadata.themoviedb.org')
#    TMDBpath = TMDBaddon.getAddonInfo('path')
#    with open('%s/tmdb.xml'%TMDBpath, 'r') as tmdbfile:
#        tmdbxml = tmdbfile.read()
#    api_key_match = re.search('\?api_key=([\da-fA-F]+)\&amp;', tmdbxml)
#    if api_key_match:
#        TMDB_KEY = api_key_match.group(1)
#        logger.info('streamondemand.buscadorall use metadata.themoviedb.org api_key')
#except Exception, e:
#    pass

TMDB_URL_BASE = 'http://api.themoviedb.org/3/'
TMDB_IMAGES_BASEURL = 'http://image.tmdb.org/t/p/'
INCLUDE_ADULT = 'true' if config.get_setting("enableadultmode") else 'false'
LANGUAGE_ID = 'it'

DTTIME = (datetime.datetime.utcnow() - datetime.timedelta(hours=5))
SYSTIME = DTTIME.strftime('%Y%m%d%H%M%S%f')
TODAY_TIME = DTTIME.strftime('%Y-%m-%d')
MONTH_TIME = (DTTIME - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
MONTH2_TIME = (DTTIME - datetime.timedelta(days=60)).strftime('%Y-%m-%d')
YEAR_DATE = (DTTIME - datetime.timedelta(days=365)).strftime('%Y-%m-%d')

TIMEOUT_TOTAL = 75

NLS_Search_by_Title = config.get_localized_string(30980)
NLS_Search_by_Person = config.get_localized_string(30981)
NLS_Search_by_Company = config.get_localized_string(30982)
NLS_Now_Playing = config.get_localized_string(30983)
NLS_Popular = config.get_localized_string(30984)
NLS_Top_Rated = config.get_localized_string(30985)
NLS_Search_by_Collection = config.get_localized_string(30986)
NLS_List_by_Genre = config.get_localized_string(30987)
NLS_Search_by_Year = config.get_localized_string(30988)
NLS_Search_Similar_by_Title = config.get_localized_string(30989)
NLS_Search_Tvshow_by_Title = config.get_localized_string(30990)
NLS_Most_Voted = config.get_localized_string(30996)
NLS_Oscar = config.get_localized_string(30997)
NLS_Last_2_months = config.get_localized_string(30998)
NLS_Library = config.get_localized_string(30991)
NLS_Next_Page = config.get_localized_string(30992)
NLS_Looking_For = config.get_localized_string(30993)
NLS_Searching_In = config.get_localized_string(30994)
NLS_Found_So_Far = config.get_localized_string(30995)
NLS_Info_Title = config.get_localized_string(30999)
NLS_Info_Person = config.get_localized_string(30979)

TMDb_genres = {}


def isGeneric():
    return True


def mainlist(item):
    logger.info("streamondemand.buscadorall mainlist")
    itemlist = [Item(channel="buscador",
                     title="[COLOR lightgreen]Cerca nei Canali...[/COLOR]",
                     action="mainlist",
                     thumbnail="http://i.imgur.com/pE5WSZp.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]%s...[/COLOR]" % NLS_Search_by_Title,
                     action="search",
                     url="search_movie_by_title",
                     thumbnail="http://i.imgur.com/B1H1G8U.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]%s...[/COLOR]" % NLS_Search_by_Person,
                     action="search",
                     url="search_person_by_name",
                     thumbnail="http://i.imgur.com/efuEeNu.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]%s...[/COLOR]" % NLS_Search_by_Year,
                     action="search",
                     url="search_movie_by_year",
                     thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/Movie%20Year.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]%s...[/COLOR]" % NLS_Search_by_Collection,
                     action="search",
                     url="search_collection_by_name",
                     thumbnail="http://i.imgur.com/JmcvZDL.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]%s...[/COLOR]" % NLS_Search_Similar_by_Title,
                     action="search",
                     url="search_similar_movie_by_title",
                     thumbnail="http://i.imgur.com/JmcvZDL.png"),
                Item(channel=__channel__,
                     title="[COLOR lime]%s...[/COLOR]" % NLS_Search_Tvshow_by_Title,
                     action="search",
                     url="search_tvshow_by_title",
                     thumbnail="https://i.imgur.com/2ZWjLn5.jpg?1"),
                Item(channel=__channel__,
                     title="(TV Shows) [COLOR lime]Ultimi Episodi - On-Air[/COLOR]",
                     action="list_tvshow",
                     url="tv/on_the_air?",
                     plot="1",
                     type="serie",
                     thumbnail="https://i.imgur.com/2ZWjLn5.jpg?1"),
                Item(channel=__channel__,
                     title="(TV Shows) [COLOR lime]Populars[/COLOR]",
                     action="list_tvshow",
                     url="tv/popular?",
                     plot="1",
                     type="serie",
                     thumbnail="https://i.imgur.com/2ZWjLn5.jpg?1"),
                Item(channel=__channel__,
                     title="(TV Shows) [COLOR lime]Top Rated[/COLOR]",
                     action="list_tvshow",
                     url="tv/top_rated?",
                     plot="1",
                     type="serie",
                     thumbnail="https://i.imgur.com/2ZWjLn5.jpg?1"),
                Item(channel=__channel__,
                     title="(TV Shows) [COLOR lime]Airing Today[/COLOR]",
                     action="list_tvshow",
                     url="tv/airing_today?",
                     plot="1",
                     type="serie",
                     thumbnail="https://i.imgur.com/2ZWjLn5.jpg?1"),
                Item(channel=__channel__,
                     title="(Movies) [COLOR yellow]%s[/COLOR]" % NLS_Now_Playing,
                     action="list_movie",
                     url="movie/now_playing?",
                     plot="1",
                     type="movie",
                     thumbnail="http://i.imgur.com/B16HnVh.png"),
                Item(channel=__channel__,
                     title="(Movies) [COLOR yellow]%s[/COLOR]" % NLS_Popular,
                     action="list_movie",
                     url="movie/popular?",
                     plot="1",
                     type="movie",
                     thumbnail="http://i.imgur.com/8IBjyzw.png"),
                Item(channel=__channel__,
                     title="(Movies) [COLOR yellow]%s[/COLOR]" % NLS_Top_Rated,
                     action="list_movie",
                     url="movie/top_rated?",
                     plot="1",
                     type="movie",
                     thumbnail="http://www.clipartbest.com/cliparts/RiG/6qn/RiG6qn79T.png"),
                Item(channel=__channel__,
                     title="(Movies) [COLOR yellow]%s[/COLOR]" % NLS_Most_Voted,
                     action="list_movie",
                     url='discover/movie?certification_country=US&sort_by=vote_count.desc&',
                     plot="1",
                     type="movie",
                     thumbnail="http://i.imgur.com/5ShnO8w.png"),
                Item(channel=__channel__,
                     title="(Movies) [COLOR yellow]%s[/COLOR]" % NLS_Oscar,
                     action="list_movie",
                     url='list/509ec17b19c2950a0600050d?',
                     plot="1",
                     type="movie",
                     thumbnail="http://i.imgur.com/5ShnO8w.png"),
                Item(channel=__channel__,
                     title="(Movies) [COLOR yellow]%s[/COLOR]" % NLS_Last_2_months,
                     action="list_movie",
                     url='discover/movie?primary_release_date.gte=%s&primary_release_date.lte=%s&' % (
                         YEAR_DATE, MONTH2_TIME),
                     plot="1",
                     type="movie",
                     thumbnail="http://i.imgur.com/CsizqUI.png"),
                Item(channel=__channel__,
                     title="(Movies) [COLOR yellow]%s[/COLOR]" % NLS_List_by_Genre,
                     action="list_genres",
                     type="movie",
                     thumbnail="http://i.imgur.com/uotyBbU.png")]

    return itemlist


def list_movie(item):
    logger.info("streamondemand.channels.database list_movie '%s/%s'" % (item.url, item.plot))

    results = [0, 0]
    page = int(item.plot)
    itemlist = build_movie_list(item, tmdb_get_data('%spage=%d&' % (item.url, page), results=results))
    if page < results[0]:
        itemlist.append(Item(
                channel=item.channel,
                title="[COLOR orange]%s (%d/%d)[/COLOR]" % (NLS_Next_Page, page * len(itemlist), results[1]),
                action="list_movie",
                url=item.url,
                plot="%d" % (page + 1),
                type=item.type,
                viewmode="" if page <= 1 else "paged_list"))

    return itemlist

def list_tvshow(item):
    logger.info("streamondemand.channels.database list_tvshow '%s/%s'" % (item.url, item.plot))

    results = [0, 0]
    page = int(item.plot)
    itemlist = build_movie_list(item, tmdb_get_data('%spage=%d&' % (item.url, page), results=results))
    if page < results[0]:
        itemlist.append(Item(
                channel=item.channel,
                title="[COLOR orange]%s (%d/%d)[/COLOR]" % (NLS_Next_Page, page * len(itemlist), results[1]),
                action="list_tvshow",
                url=item.url,
                plot="%d" % (page + 1),
                type=item.type,
                viewmode="" if page <= 1 else "paged_list"))

    return itemlist

def list_genres(item):
    logger.info("streamondemand.channels.database list_genres")

    tmdb_genre(1)
    itemlist = []
    for genre_id, genre_name in TMDb_genres.iteritems():
        itemlist.append(
                Item(channel=item.channel,
                     title=genre_name,
                     action="list_movie",
                     url='genre/%d/movies?primary_release_date.gte=%s&primary_release_date.lte=%s&' % (
                         genre_id, YEAR_DATE, TODAY_TIME),
                     plot="1"))

    return itemlist


# Do not change the name of this function otherwise launcher.py won't create the keyboard dialog required to enter the search terms
def search(item, search_terms):
    if item.url == '': return []

    return globals()[item.url](item, search_terms) if item.url in globals() else []


def search_tvshow_by_title(item, search_terms):
    logger.info("streamondemand.channels.database search_tvshow_by_title '%s'" % (search_terms))

    return list_movie(
        Item(channel=item.channel,
             url='search/tv?query=%s&' % url_quote_plus(search_terms),
             plot="1",
             type="serie"))


def search_movie_by_title(item, search_terms):
    logger.info("streamondemand.channels.database search_movie_by_title '%s'" % (search_terms))

    return list_movie(
        Item(channel=item.channel,
             url='search/movie?query=%s&' % url_quote_plus(search_terms),
             plot="1",
             type="movie"))


def search_similar_movie_by_title(item, search_terms):
    logger.info("streamondemand.channels.database search_movie_by_title '%s'" % (search_terms))

    return list_movie(
        Item(channel=item.channel,
             url='search/movie?append_to_response=similar_movies,alternative_title&query=%s&' % url_quote_plus(search_terms),
             plot="1",
             type='movie'))


def search_movie_by_year(item, search_terms):
    logger.info("streamondemand.channels.database search_movie_by_year '%s'" % (search_terms))

    year = url_quote_plus(search_terms)
    result = []
    if len(year) == 4:
        result.extend(
            list_movie(
                Item(channel=item.channel,
                     url='discover/movie?primary_release_year=%s&' % year,
                     plot="1",
                     type="movie")))
    return result


def search_person_by_name(item, search_terms):
    logger.info("streamondemand.channels.database search_person_by_name '%s'" % (search_terms))

    persons = tmdb_get_data("search/person?query=%s&" % url_quote_plus(search_terms))

    itemlist = []
    for person in persons:
        name = normalize_unicode(tmdb_tag(person, 'name'))
        poster = tmdb_image(person, 'profile_path')
        fanart = ''
        for movie in tmdb_tag(person, 'known_for', []):
            if tmdb_tag_exists(movie, 'backdrop_path'):
                fanart = tmdb_image(movie, 'backdrop_path', 'w1280')
                break

        # extracmds = [
        #     (NLS_Info_Person, "RunScript(script.extendedinfo,info=extendedactorinfo,id=%s)" % str(tmdb_tag(person, 'id')))] \
        #     if xbmc.getCondVisibility('System.HasAddon(script.extendedinfo)') else []

        itemlist.append(Item(
                channel=item.channel,
                action='search_movie_by_person',
                extra=str(tmdb_tag(person, 'id')),
                title=name,
                thumbnail=poster,
                viewmode='list',
                fanart=fanart,
                type='movie'
                # extracmds=extracmds
        ))

    return itemlist


def search_movie_by_person(item):
    logger.info("streamondemand.channels.database search_movie_by_person '%s'" % (item.extra))

    # return list_movie(
    #     Item(channel=item.channel,
    #          url="discover/movie?with_people=%s&primary_release_date.lte=%s&sort_by=primary_release_date.desc&" % (
    #              item.extra, TODAY_TIME),
    #          plot="1"))

    person_movie_credits = tmdb_get_data(
            "person/%s/movie_credits?primary_release_date.lte=%s&sort_by=primary_release_date.desc&" % (
                item.extra, TODAY_TIME))
    movies = []
    if person_movie_credits:
        movies.extend(tmdb_tag(person_movie_credits, 'cast', []))
        movies.extend(tmdb_tag(person_movie_credits, 'crew', []))

    # Movie person list is not paged
    return build_movie_list(item, movies)


def search_collection_by_name(item, search_terms):
    logger.info("streamondemand.channels.database search_collection_by_name '%s'" % (search_terms))

    collections = tmdb_get_data("search/collection?query=%s&" % url_quote_plus(search_terms))

    itemlist = []
    for collection in collections:
        name = normalize_unicode(tmdb_tag(collection, 'name'))
        poster = tmdb_image(collection, 'poster_path')
        fanart = tmdb_image(collection, 'backdrop_path', 'w1280')

        itemlist.append(Item(
                channel=item.channel,
                action='search_movie_by_collection',
                extra=str(tmdb_tag(collection, 'id')),
                title=name,
                thumbnail=poster,
                viewmode='list',
                fanart=fanart,
                type='movie'
        ))

    return itemlist


def search_movie_by_collection(item):
    logger.info("streamondemand.channels.database search_movie_by_collection '%s'" % (item.extra))

    collection = tmdb_get_data("collection/%s?" % item.extra)

    # Movie collection list is not paged
    return build_movie_list(item, collection['parts']) if 'parts' in collection else []


def build_movie_list(item, movies):
    if movies is None: return []

    itemlist = []
    for movie in movies:
        t = tmdb_tag(movie, 'title')
        if t == '':
            t = re.sub('\s(|[(])(UK|US|AU|\d{4})(|[)])$', '', tmdb_tag(movie, 'name'))
        title = normalize_unicode(t)
        title_search = normalize_unicode(t, encoding='ascii')
        poster = tmdb_image(movie, 'poster_path')
        fanart = tmdb_image(movie, 'backdrop_path', 'w1280')
        jobrole = normalize_unicode(
                ' [COLOR yellow][' + tmdb_tag(movie, 'job') + '][/COLOR]' if tmdb_tag_exists(movie, 'job') else '')
        genres = normalize_unicode(
            ' / '.join([tmdb_genre(genre).upper() for genre in tmdb_tag(movie, 'genre_ids', [])]))
        year = tmdb_tag(movie, 'release_date')[0:4] if tmdb_tag_exists(movie, 'release_date') else ''
        plot = normalize_unicode(tmdb_tag(movie, 'overview'))
        rating = tmdb_tag(movie, 'vote_average')
        votes = tmdb_tag(movie, 'vote_count')

        extrameta = {'plot': plot}
        if year != "": extrameta["Year"] = year
        if genres != "": extrameta["Genre"] = genres
        if votes:
            extrameta["Rating"] = rating
            extrameta["Votes"] = "%d" % votes

        # extracmds = [(NLS_Info_Title, "RunScript(script.extendedinfo,info=extendedinfo,id=%s)" % str(tmdb_tag(movie, 'id')))] \
        #     if xbmc.getCondVisibility('System.HasAddon(script.extendedinfo)') else [('Movie/Show Info', 'XBMC.Action(Info)')]

        found = False
        kodi_db_movies = kodi_database_movies(title)
        for kodi_db_movie in kodi_db_movies:
            logger.info('streamondemand.database set for local playing(%s):\n%s' % (title, str(kodi_db_movie)))
            if year == str(kodi_db_movie["year"]):
                found = True

                # If some, less relevant, keys are missing locally
                # try to get them through TMDB anyway.
                try:
                    poster = kodi_db_movie["art"]["poster"]
                    fanart = kodi_db_movie["art"]["fanart"]
                except KeyError:
                    poster = poster
                    fanart = fanart

                itemlist.append(Item(
                        channel=item.channel,
                        action='play',
                        url=kodi_db_movie["file"],
                        title='[COLOR orange][%s][/COLOR] ' % NLS_Library + kodi_db_movie["title"] + jobrole,
                        thumbnail=poster,
                        category=genres,
                        plot=plot,
                        viewmode='movie_with_plot',
                        fanart=fanart,
                        infoLabels=extrameta,
                        folder=False,
                ))

        if not found:
            logger.info('streamondemand.database set for channels search(%s)' % title)
            itemlist.append(Item(
                    channel=item.channel,
                    action='do_channels_search',
                    extra=title_search + '{}' + item.type + '{}' + year,
                    title=title + jobrole,
                    thumbnail=poster,
                    category=genres,
                    plot=plot,
                    viewmode='movie_with_plot',
                    fanart=fanart,
                    infoLabels=extrameta,
            ))

    return itemlist


def normalize_unicode(string, encoding='utf-8'):
    if string is None: string = ''
    return normalize('NFKD', string if isinstance(string, unicode) else unicode(string, encoding, 'ignore')).encode(
            encoding, 'ignore')


def tmdb_get_data(url="", results=[0, 0], language=True):
    url = TMDB_URL_BASE + "%sinclude_adult=%s&api_key=%s" % (url, INCLUDE_ADULT, TMDB_KEY)
    # Temporary fix until tmdb fixes the issue with getting the genres by language!
    if language: url += "&language=%s" % LANGUAGE_ID
    response = get_json_response(url)
    results[0] = response['total_pages'] if 'total_pages' in response else 0
    results[1] = response['total_results'] if 'total_results' in response else 0

    if response:
        if "results" in response:
            return response["results"]
        elif "items" in response:
            return response["items"]
        elif "tv_credits" in response:
            return response["tv_credits"]["cast"]
        else:
            return response


def tmdb_tag_exists(entry, tag):
    return tag in entry and entry[tag] is not None


def tmdb_tag(entry, tag, default=""):
    return entry[tag] if isinstance(entry, dict) and tag in entry else default


def tmdb_image(entry, tag, width='original'):
    return TMDB_IMAGES_BASEURL + width + '/' + tmdb_tag(entry, tag) if tmdb_tag_exists(entry, tag) else ''


def tmdb_genre(id):
    if id not in TMDb_genres:
        genres = tmdb_get_data("genre/list?", language=False)
        for genre in tmdb_tag(genres, 'genres', []):
            TMDb_genres[tmdb_tag(genre, 'id')] = tmdb_tag(genre, 'name')

    return TMDb_genres[id] if id in TMDb_genres and TMDb_genres[id] != None else str(id)


def kodi_database_movies(title):
    json_query = \
        '{"jsonrpc": "2.0",\
            "params": {\
               "sort": {"order": "ascending", "method": "title"},\
               "filter": {"operator": "is", "field": "title", "value": "%s"},\
               "properties": ["title", "art", "file", "year"]\
            },\
            "method": "VideoLibrary.GetMovies",\
            "id": "libMovies"\
        }' % title
    response = get_xbmc_jsonrpc_response(json_query)
    return response["result"]["movies"] if response and "result" in response and "movies" in response["result"] else []


def get_xbmc_jsonrpc_response(json_query=""):
    try:
        response = xbmc.executeJSONRPC(json_query)
        response = unicode(response, 'utf-8', errors='ignore')
        response = json.loads(response)
        logger.info("streamondemand.channels.database jsonrpc %s" % response)
    except Exception, e:
        logger.info("streamondemand.channels.database jsonrpc error: %s" % str(e))
        response = None
    return response


def url_quote_plus(input_string):
    try:
        return urllib.quote_plus(input_string.encode('utf8', 'ignore'))
    except:
        return urllib.quote_plus(unicode(input_string, "utf-8").encode("utf-8"))


def get_json_response(url=""):
    response = scrapertools.cache_page(url)
    try:
        results = json.loads(response)
    except:
        logger.info("streamondemand.channels.database Exception: Could not get new JSON data from %s" % url)
        results = []
    return results


def channel_search(queue, channel_parameters, category, title_year, tecleado):
    try:
        search_results = []

        exec "from channels import " + channel_parameters["channel"] + " as module"
        mainlist = module.mainlist(Item(channel=channel_parameters["channel"]))

        for item in mainlist:
            if item.action != "search" or category and item.extra != category:
                continue

            for res_item in module.search(item.clone(), tecleado):
                title = res_item.fulltitle

                # If the release year is known, check if it matches the year found in the title
                if title_year > 0:
                    year_match = re.search('\(.*(\d{4}).*\)', title)
                    if year_match and abs(int(year_match.group(1)) - title_year) > 1:
                        continue

                # Clean up a bit the returned title to improve the fuzzy matching
                title = re.sub(r'\(.*\)', '', title)  # Anything within ()
                title = re.sub(r'\[.*\]', '', title)  # Anything within []

                # Check if the found title fuzzy matches the searched one
                if fuzz.token_sort_ratio(tecleado, title) > 85:
                    res_item.title = "[COLOR azure]" + res_item.title + "[/COLOR][COLOR orange] su [/COLOR][COLOR green]" + channel_parameters["title"] + "[/COLOR]"
                    search_results.append(res_item)

        queue.put(search_results)

    except:
        logger.error("No se puede buscar en: " + channel_parameters["title"])
        import traceback
        logger.error(traceback.format_exc())


def do_channels_search(item):
    logger.info("streamondemand.channels.buscadorall do_channels_search")

    tecleado, category, title_year = item.extra.split('{}')

    try:
        title_year = int(title_year)
    except:
        title_year = 0

    itemlist = []

    channels_path = os.path.join(config.get_runtime_path(), "channels", '*.xml')
    logger.info("streamondemand.channels.buscador channels_path=" + channels_path)

    channel_language = config.get_setting("channel_language")
    logger.info("streamondemand.channels.buscador channel_language=" + channel_language)
    if channel_language == "":
        channel_language = "all"
        logger.info("streamondemand.channels.buscador channel_language=" + channel_language)

    progreso = platformtools.dialog_progress_bg(NLS_Looking_For % tecleado)

    channel_files = glob.glob(channels_path)

    search_results = Queue.Queue()
    number_of_channels = 0

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

        t = Thread(target=channel_search, args=[search_results, channel_parameters, category, title_year, tecleado])
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
